import asyncio
import datetime
import logging
import time
from dataclasses import dataclass, field

from twitchAPI.helper import first
from twitchAPI.object import Clip as TwitchClip
from twitchAPI.object import CreatedClip, TwitchUser
from twitchAPI.twitch import Twitch

from snapper.database import Clip, Keyword, Stream, TransactionHandler
from snapper.irc import IRCClient
from snapper.util import Color, colored_string


class MessagePrefixLogger(logging.LoggerAdapter):
    """
    Custom logger adapter to prepend a prefix to each log message.
    """

    def process(self, msg, kwargs):
        prefix = self.extra["prefix"] if self.extra is not None else ""
        return f"{prefix}: {msg}", kwargs


@dataclass(repr=True)
class KeywordData:
    """
    Simple data class that is used as value for the keyword map.
    It contains information to a specific keyword (or rather emote)
    """

    count: int = 0
    is_active: bool = False
    active_intervals: int = 0
    timestamp_activated: str | None = field(default=None)

    def activate(self):
        self.is_active = True
        self.active_intervals = 1
        self.timestamp_activated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def deactivate(self):
        self.is_active = False
        self.active_intervals = 0
        self.timestamp_activated = None
        self.count = 0


class StreamObserver:
    """
    Class that wrapped the IRC channel and its running co-routine-loop,
    the processing of those message from the message queue and the logic to recognize special moments
    in the stream by counting emotes in order to eventually invoke a trigger (for example the creation of a clip)
    """

    def __init__(self, twitch: Twitch, stream: Stream):
        """Constructor

        Args:
            twitch_channel_name (str): The name of the channel, same as twitch.tv/<lirik>
            twitch (Twitch): An initialized twitchAPI object
        """
        self.twitch = twitch
        self.stream = stream
        self.msg_queue: asyncio.Queue = asyncio.Queue()
        self.last_time_triggered: float = 0
        self.keyword_count = {
            keyword: KeywordData() for keyword in self.stream.keywords
        }
        self.running = False
        self.Log = MessagePrefixLogger(
            logging.getLogger(__name__), {"prefix": self.stream.channel_name}
        )

        assert (
            self.stream.activation_time_window >= self.stream.pause_interval
        ), "ACTIVATION_INTERVAL has to be >= than PAUSE_INTERVAL"
        assert (
            self.stream.activation_time_window % self.stream.pause_interval == 0
        ), "ACTIVATION_INTERVAL has to be a multiply of PAUSE_INTERVAL"

    async def start_observing(self) -> None:
        irc_client = IRCClient.from_channel_name_only(
            self.stream.channel_name,
            self.msg_queue,
        )

        self.running = True
        # store hard references because asyncio only does weak references
        self._irc_task = asyncio.create_task(irc_client.start_and_listen())
        self._analyse_task = asyncio.create_task(self._analyse_keyword_count())
        self._queue_task = asyncio.create_task(self._message_queue_consumer())

    def stop_observing(self):
        self.running = False

    async def _message_queue_consumer(self):
        """
        "Subscribes" the queue that the IRC channel fills up with chat messages,
        reads them and increase the keyword counts accordingly.
        """
        while self.running:
            message = await self.msg_queue.get()
            if message is None:
                return
            for keyword, keyword_data in self.keyword_count.items():
                if keyword.value in message.message:
                    keyword_data.count += 1
                    self.Log.debug(
                        f"{keyword.value} count increased to: {keyword_data.count}"
                    )
            self.Log.debug(message)

    async def _analyse_keyword_count(self):
        """
        Recognizes when a special event happened in the stream by continously analysing the keyword map that has
        the list of observed keywords and their corresponding count in it.
        It works by checking if a keyword is mentioned at least X times in the last Y seconds, to
        change this keyword in the "active" mode. Then it will count how many times this keyword is sent in a longer timespan Z.
        Finally, if this value is high enough it will invoke a trigger.

        We do the previous activate state change in order to avoid rolling windows. Just using, e.g. 15 seconds intervals
        can potentially backfire if the special stream event happens right between two intervals.
        """
        # Every loop is a "pause"-interval
        while self.running:
            # Check every keyword (emote)
            for keyword, keyword_data in self.keyword_count.items():
                self.Log.debug(
                    colored_string(
                        f"{keyword_data.count}x{keyword.value} per {self.stream.pause_interval} seconds",
                        Color.RED,
                    )
                )
                await self._check_keyword(keyword, keyword_data)

            await asyncio.sleep(self.stream.pause_interval)

    async def _check_keyword(self, keyword: Keyword, keyword_data: KeywordData):
        # When the keyword is not in activate-status, check if the keyword is mentioned enough times in the last
        # "pause"-interval in order to activate the keyword.
        # Otherwise reset the count again, start from 0 for the next interval
        if not keyword_data.is_active:
            # Check trigger threshold and if the last trigger happened some time ago to not spam triggers (and potential clips)
            if keyword_data.count >= 3 and self._is_trigger_ready_again():
                self.Log.info(
                    colored_string(
                        f"Activate {keyword.value}!",
                        Color.YELLOW,
                    )
                )
                keyword_data.activate()
            # When keyword is not active, the count of used emotes should reset for every "pause"-interval
            else:
                keyword_data.count = 0
        # Keyword is already active
        else:
            # The loop is fixed by the smallest "sleep" value, the "pause"-interval, so in order to
            # make the "count for a longer time period"-logic work, it has to be a multiply of this value
            # and we need to save the amount of run-through intervals
            keyword_data.active_intervals += 1
            # Counted amount of keywords in the activation time window, this time frame is now over
            if (
                keyword_data.active_intervals
                >= self.stream.activation_time_window / self.stream.pause_interval
            ):
                await self._activation_time_window_ended(keyword, keyword_data)

    async def _activation_time_window_ended(
        self, keyword: Keyword, keyword_data: KeywordData
    ):
        self.Log.info(
            colored_string(
                f"After {self.stream.activation_time_window} seconds, \
                {keyword} was mentioned {keyword_data.count} times",
                Color.YELLOW,
            )
        )
        # The amount counted is high enough to finally invoke the trigger.
        # Something special happened in the stream when this triggers, create a clip or sth
        if keyword_data.count >= self.stream.trigger_threshold:
            await self._invoke_trigger(keyword, keyword_data)
        keyword_data.deactivate()

    async def _invoke_trigger(self, keyword: Keyword, keyword_data: KeywordData):
        self.Log.info("Do something, e.g. create clip")
        try:
            twitch_clip: TwitchClip = await self._create_clip()
            # Save the clip to the database using async session
            new_clip: Clip = Clip(
                twitch_clip_id=twitch_clip.id,
                stream=self.stream,
                thumbnail_url=twitch_clip.thumbnail_url,
                title=twitch_clip.title,
                view_count=twitch_clip.view_count,
                keyword_trigger=keyword,
                keyword_count=keyword_data.count,
            )
            await TransactionHandler.persist(new_clip)
            self.Log.info(f"Saving clip to database! {vars(new_clip)}")
        except Exception as e:
            self.Log.error(e)

    def _is_trigger_ready_again(self) -> bool:
        """
        Checks if the last trigger is far enough in the past to not spawn the
        creation of clips or other possible triggers.

        Returns:
            bool: Whether the stream might invoke a trigger again or not
        """
        last_trigger_time: float = time.time() - self.last_time_triggered
        if last_trigger_time < self.stream.min_trigger_pause:
            self.Log.warn(
                f"Triggered on channel {self.stream.channel_name}, but last trigger was {last_trigger_time} seconds ago,  \
                but MIN_TRIGGER_PAUSE is {self.stream.min_trigger_pause}."
            )
            return False
        else:
            self.last_time_triggered = time.time()
            return True

    async def _create_clip(
        self,
    ) -> TwitchClip:
        """
        Uses the twitchAPI to create a clip right after the moment the special event was
        notices by the trigger logic.

        Raises:
            Exception:  Mainly due to API errors if there no broadcast_id can be found,
                        the twitch clip creation failed, or clip could not be saved to DB

        Returns:
            str | None: The ID of the clip or None if an exception happend.
        """

        user_info: TwitchUser | None = await first(
            self.twitch.get_users(logins=[self.stream.channel_name])
        )
        if not user_info:
            raise Exception(
                f"Cannot extract broadcast_id for channel {self.stream.channel_name}."
            )

        try:
            created_clip: CreatedClip = await self.twitch.create_clip(
                user_info.id, has_delay=True
            )
        except Exception as _:
            raise Exception(
                f"Cannot create clip for the the broadcaster with id={user_info.id}"
            )

        self.Log.info(
            f"Created clip with id: {created_clip.id} and edit-url {created_clip.edit_url}"
        )

        clip: TwitchClip | None = None
        while (
            clip := await first(self.twitch.get_clips(clip_id=[created_clip.id]))
        ) is None:
            await asyncio.sleep(1)

        return clip
