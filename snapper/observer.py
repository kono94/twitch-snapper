import asyncio
import datetime
import logging
import time
from dataclasses import dataclass

from twitchAPI.helper import first
from twitchAPI.object import Clip, CreatedClip, TwitchUser
from twitchAPI.twitch import Twitch

from snapper.database import AsyncSessionLocal, Clip
from snapper.irc import IRCClient
from snapper.util import Color, clip_to_string, colored_string, get_envs

Log = logging.getLogger(__name__)


@dataclass
class KeywordData:
    """
    Simple data class that is used as value for the keyword map.
    It contains information to a specific keyword (or rather emote)
    """

    count: int
    is_active: bool
    active_intervals: int
    timestamp_activated: str | None

    def activate(self):
        self.is_active = True
        self.active_intervals = 1
        self.timestamp_activated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def deactivate(self):
        self.is_active = False
        self.active_intervals = 0
        self.timestamp_activated = None
        self.count = 0

    def __str__(self) -> str:
        return f"count: {self.count} \t isActive: {self.is_active} \t active_intervals: {self.active_intervals}\
                \t timestamp_activated: {self.timestamp_activated}"


class StreamObserver:
    """
    Class that wrapped the IRC channel and its running co-routine-loop,
    the processing of those message from the message queue and the logic to recognize special moments
    in the stream by counting emotes in order to eventually invoke a trigger (for example the creation of a clip)
    """

    def __init__(self, twitch_channel_name: str, twitch: Twitch):
        """Constructor

        Args:
            twitch_channel_name (str): The name of the channel, same as twitch.tv/<lirik>
            twitch (Twitch): An initialized twitchAPI object
        """
        self.twitch_channel_name = twitch_channel_name
        self.twitch: Twitch = twitch
        self.msg_queue: asyncio.Queue = asyncio.Queue()
        self.keyword_list = [
            "LUL",
            "KEKW",
            "Pog",
        ]
        self.PAUSE_INTERVAL = 3
        self.ACTIVATION_THRESHOLD = 4
        self.ACTIVATION_TIME_WINDOW = 15
        assert (
            self.ACTIVATION_TIME_WINDOW >= self.PAUSE_INTERVAL
        ), "ACTIVATION_INTERVAL has to be >= than PAUSE_INTERVAL"
        assert (
            self.ACTIVATION_TIME_WINDOW % self.PAUSE_INTERVAL == 0
        ), "ACTIVATION_INTERVAL has to be a multiply of PAUSE_INTERVAL"
        self.TRIGGER_THRESHOLD = 30
        self.MIN_TRIGGER_INTERVAL = 60
        self.last_time_triggered: float = 0
        self.keyword_count = {
            keyword: KeywordData(0, False, 0, None) for keyword in self.keyword_list
        }
        self.running = False

    async def start_observing(self) -> None:
        irc_client = IRCClient.from_channel_name_only(
            self.twitch_channel_name,
            self.msg_queue,
        )

        self.running = True
        asyncio.get_event_loop().create_task(irc_client.start_and_listen())
        asyncio.get_event_loop().create_task(self._analyse_keyword_count())
        asyncio.get_event_loop().create_task(self._message_queue_consumer())

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
                if keyword in message.message:
                    keyword_data.count += 1
                    Log.debug(f"{keyword} count increased to: {keyword_data.count}")
            Log.debug(message)

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
                Log.debug(
                    colored_string(
                        f"{keyword_data.count}x{keyword} per {self.PAUSE_INTERVAL} seconds",
                        Color.RED,
                    )
                )
                await self._check_keyword(keyword, keyword_data)

            await asyncio.sleep(self.PAUSE_INTERVAL)

    async def _check_keyword(self, keyword: str, keyword_data: KeywordData):
        # When the keyword is not in activate-status, check if the keyword is mentioned enough times in the last
        # "pause"-interval in order to activate the keyword.
        # Otherwise reset the count again, start from 0 for the next interval
        if not keyword_data.is_active:
            # Check trigger threshold and if the last trigger happened some time ago to not spam triggers (and potential clips)
            if keyword_data.count >= 3 and self._is_trigger_ready_again():
                Log.info(
                    colored_string(
                        f"Activate {keyword}!",
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
                >= self.ACTIVATION_TIME_WINDOW / self.PAUSE_INTERVAL
            ):
                await self._activation_time_window_ended(keyword, keyword_data)

    async def _activation_time_window_ended(
        self, keyword: str, keyword_data: KeywordData
    ):
        Log.info(
            colored_string(
                f"After {self.ACTIVATION_TIME_WINDOW} seconds, \
                {keyword} was mentioned {keyword_data.count} times",
                Color.YELLOW,
            )
        )
        # The amount counted is high enough to finally invoke the trigger.
        # Something special happened in the stream when this triggers, create a clip or sth
        if keyword_data.count >= self.TRIGGER_THRESHOLD:
            await self._invoke_trigger(keyword, keyword_data)
        keyword_data.deactivate()

    async def _invoke_trigger(self, keyword: str, keyword_data: KeywordData):
        Log.info("Do something, e.g. create clip")
        try:
            await self._create_clip(keyword, keyword_data.count)
        except Exception as e:
            Log.error(e)

    def _is_trigger_ready_again(self) -> bool:
        """
        Checks if the last trigger is far enough in the past to not spawn the
        creation of clips or other possible triggers.

        Returns:
            bool: Whether the stream might invoke a trigger again or not
        """
        last_trigger_time: float = time.time() - self.last_time_triggered
        if last_trigger_time < self.MIN_TRIGGER_INTERVAL:
            Log.warn(
                f"Triggered on channel {self.twitch_channel_name}, but last trigger was {last_trigger_time} seconds ago,  \
                but MIN_TRIGGER_INTERVAL is {self.MIN_TRIGGER_INTERVAL}."
            )
            return False
        else:
            self.last_time_triggered = time.time()
            return True

    async def _create_clip(self, keyword: str, keyword_amount: int) -> str:
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
            self.twitch.get_users(logins=[self.twitch_channel_name])
        )
        if not user_info:
            raise Exception(
                f"Cannot extract broadcast_id for channel {self.twitch_channel_name}."
            )

        createdClip: CreatedClip = await self.twitch.create_clip(
            user_info.id, has_delay=True
        )
        Log.info(
            f"Created clip with id: {createdClip.id} and edit-url {createdClip.edit_url}"
        )
        # Save the clip to the database using async session
        async with AsyncSessionLocal() as session:
            new_clip = Clip(
                channel_name=self.twitch_channel_name,
                clip_id=createdClip.id,
                keyword_trigger=keyword,
                keyword_amount=keyword_amount,
            )
            session.add(new_clip)
            await session.commit()

        return createdClip.id

        # clip: Clip | None = await first(self.twitch.get_clips(clip_id=[createdClip.id]))
