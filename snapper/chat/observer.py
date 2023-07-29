import asyncio
import datetime
import logging
from dataclasses import dataclass

from snapper.chat.irc import IRCClient
from snapper.util import Color, colored_string, get_envs

Log = logging.getLogger(__name__)


@dataclass
class KeywordData:
    count: int
    is_active: bool
    active_circles: int
    timestamp_activated: str | None

    def activate(self):
        self.is_active = True
        self.active_circles = 1
        self.timestamp_activated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def deactivate(self):
        self.is_active = False
        self.active_circles = 0
        self.timestamp_activated = None
        self.count = 0

    def __str__(self) -> str:
        return f"count: {self.count} \t isActive: {self.is_active} \t active_circles: {self.active_circles} \t timestamp_activated: {self.timestamp_activated}"


class StreamObserver:
    def __init__(self, twitch):
        self.twitch = twitch
        self.msg_queue = asyncio.Queue()
        self.keyword_list = ["LUL", "KEKW"]
        self.TRIGGER_THRESHOLD = 30
        self.keyword_count = {
            k: KeywordData(0, False, 0, None) for k in self.keyword_list
        }
        self.running = False

    async def start_observing(self) -> None:
        envs = get_envs()

        Log.debug("IRC OAUTH: %s", {envs["IRC_OAUTH"]})

        irc_client = IRCClient(
            envs["IRC_HOST"],
            int(envs["IRC_PORT"]),
            envs["IRC_NICKNAME"],
            envs["IRC_OAUTH"],
            envs["IRC_CHANNEL"],
            self.msg_queue,
        )

        self.running = True
        asyncio.get_event_loop().create_task(irc_client.start_and_listen())
        asyncio.get_event_loop().create_task(self._analyse_keyword_count())
        asyncio.get_event_loop().create_task(self._message_listener())

    def stop_observing(self):
        self.running = False

    async def _analyse_keyword_count(self):
        pause = 3
        while self.running:
            for keyword, keyword_data in self.keyword_count.items():
                Log.debug(
                    colored_string(
                        f"{keyword_data.count}x{keyword} per {pause} seconds", Color.RED
                    )
                )
                if not keyword_data.is_active and keyword_data.count >= 3:
                    Log.info(f"Activated {keyword}!")
                    keyword_data.activate()
                elif not keyword_data.is_active:
                    keyword_data.count = 0
                else:
                    keyword_data.active_circles += 1
                    if keyword_data.active_circles >= 5:
                        Log.info(
                            f"After {pause * keyword_data.active_circles} seconds, \
                                    {keyword} was mentioned {keyword} times"
                        )
                        if keyword_data.count >= self.TRIGGER_THRESHOLD:
                            Log.info("Do something, e.g. create clip")
                            await self._triggered(self.twitch)
                        keyword_data.deactivate()

            await asyncio.sleep(pause)

    async def _message_listener(self):
        while self.running:
            message = await self.msg_queue.get()
            if message is None:
                return
            for keyword, keyword_data in self.keyword_count.items():
                if keyword in message.message:
                    keyword_data.count += 1
                    print(f"{keyword} count increased to: {keyword_data.count}")
            Log.debug(message)

    async def _triggered(self, twitch):
        clip = await twitch.create_clip("lirik")
        pass
