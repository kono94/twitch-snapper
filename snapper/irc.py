import asyncio
import datetime
import logging
from dataclasses import dataclass
from enum import Enum

from snapper.util import get_envs

Log = logging.getLogger(__name__)


class IRCCommand(Enum):
    JOIN = "JOIN"
    MESSAGE = "PRIVMSG"


@dataclass
class IRCMessage:
    timestamp: str
    username: str
    message: str

    def __str__(self) -> str:
        return f"Username: {self.username} \t Message: {self.message}"


class IRCClient:
    @classmethod
    def from_channel_name_only(cls, channel: str, coroutine_queue: asyncio.Queue):
        envs = get_envs()
        return cls(
            envs["IRC_HOST"],
            int(envs["IRC_PORT"]),
            envs["IRC_NICKNAME"],
            envs["IRC_OAUTH"],
            channel,
            coroutine_queue,
        )

    def __init__(
        self,
        host: str,
        port: int,
        nick: str,
        oauth: str,
        channel: str,
        coroutine_queue: asyncio.Queue,
    ):
        super().__init__()
        self.HOST = host
        self.PORT = port
        self.NICK = nick
        self.PASSWORD = oauth
        self.channel = channel
        self.coroutine_queue = coroutine_queue

    async def start_and_listen(self):
        await self.connect()
        Log.debug(f"Waiting for messages in channel {self.channel}...")
        await self._read_messages()

    async def connect(self):
        Log.debug("Connecting to Twitch chat...")
        self.reader, self.writer = await self._open_connection()
        Log.debug("Connection established!")
        await self._join_channel(self.channel)

    async def _join_channel(self, channel):
        await self._send_message("PASS " + self.PASSWORD)
        await self._send_message("NICK " + self.NICK)
        await self._send_message("USER " + self.NICK + " 8 * :" + self.NICK)
        Log.debug(f"Joining channel {channel}...")
        await self._send_message("JOIN #" + channel)

    async def _send_message(self, message: str) -> None:
        self.writer.write((message + "\r\n").encode())
        await self.writer.drain()

    async def _open_connection(
        self,
    ) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        return await asyncio.open_connection(self.HOST, self.PORT)

    async def _read_messages(self):
        while True:
            try:
                line = await self.reader.readline()
            except Exception as err:
                # try to reconnect
                Log.warn(err)
                await asyncio.sleep(2)
                await self.connect()
                continue

            line = line.decode().strip()
            if line == "":
                continue
            command = line.split(" ")[1]
            if command == IRCCommand.MESSAGE.value:
                username_start = line.index("!") + 1
                username_end = line.index("@")
                username = line[username_start:username_end]
                message_start = line.index(f"PRIVMSG #{self.channel} :") + len(
                    f"PRIVMSG #{self.channel} :"
                )
                message = line[message_start:]
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await self.coroutine_queue.put(
                    IRCMessage(timestamp=now, username=username, message=message)
                )
            elif line.startswith("PING"):
                await self._send_message(line.replace("PING", "PONG"))
