from enum import Enum
import socket
import threading
import datetime
from dataclasses import dataclass


class IRCCommand(Enum):
    JOIN = "JOIN"
    MESSAGE = "PRIVMSG"


@dataclass
class IRCMessage:
    timestamp: str
    username: str
    message: str

    def __str__(self) -> str:
        return f"{self.timestamp} - Username: {self.username} Message: {self.message}"


class IRCClient(threading.Thread):
    def __init__(self, host, port, nick, password, channel, callback=None):
        super().__init__()
        self.host = host
        self.port = port
        self.nick = nick
        self.password = password
        self.channel = channel
        self.callback = callback

    def send_message(self, message):
        self.sock.send((message + "\r\n").encode())

    def join_channel(self, channel):
        self.send_message("JOIN #" + channel)

    def process_line(self, line):
        command = line.split(" ")[1]
        if command == IRCCommand.MESSAGE.value:
            username_start = line.index("!") + 1
            username_end = line.index("@")
            username = line[username_start:username_end]
            message_start = line.index(f"PRIVMSG #{self.channel} :")
            message = line[message_start:]
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return IRCMessage(timestamp=now, username=username, message=message)
        elif line.startswith("PING"):
            self.send_message(line.replace("PING", "PONG"))

    def run(self):
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))
        self.send_message("PASS " + self.password)
        self.send_message("NICK " + self.nick)
        self.send_message("USER " + self.nick + " 8 * :" + self.nick)
        self.join_channel(self.channel)

        while True:
            data = b""
            while not data.endswith(b"\r\n"):
                new_data = self.sock.recv(124)
                if not new_data:
                    break
                data += new_data
            lines = data.decode().strip().split("\r\n")
            for line in lines:
                if self.callback is not None:
                    self.callback(self.process_line(line))


HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = "lul_snapper"
PASS = "oauth:xh39ad8j7l9uxsxym67fsjqn5mc57z"
CHAN = "fps_shaka"


def on_received(message):
    print(message)


irc_client = IRCClient(HOST, PORT, NICK, PASS, CHAN, callback=on_received)
irc_client.start()
