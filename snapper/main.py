import datetime
import logging
import sys
import threading
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass

from snapper.chat.irc import IRCClient, IRCMessage
from snapper.util import get_envs


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


def main() -> None:
    Log = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    Log.debug("This is main!")
    envs = get_envs()
    Log.debug("IRC OAUTH: %s", {envs["IRC_OAUTH"]})

    TRIGGER_THRESHOLD = 30
    keyword_list: list[str] = ["LUL", "KEKW"]
    keyword_count: dict[str, KeywordData] = {}
    for k in keyword_list:
        keyword_count[k] = KeywordData(0, False, 0, None)

    lock = threading.Lock()

    def analyse_keyword_count():
        pause = 3
        while True:
            with lock:
                for keyword, keyword_data in keyword_count.items():
                    print(f"{keyword_data.count}x{keyword} per {pause} seconds")
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
                            if keyword_data.count >= TRIGGER_THRESHOLD:
                                Log.info("Do something, e.g. create clip")
                            keyword_data.deactivate()
            time.sleep(pause)

    threading.Thread(target=analyse_keyword_count).start()

    def on_received(message: IRCMessage):
        if message is None:
            return
        for keyword, keyword_data in keyword_count.items():
            if keyword in message.message:
                with lock:
                    keyword_data.count += 1
                    print(f"{keyword} count increased to: {keyword_data.count}")

    # Log.debug(message)

    irc_client = IRCClient(
        envs["IRC_HOST"],
        int(envs["IRC_PORT"]),
        envs["IRC_NICKNAME"],
        envs["IRC_OAUTH"],
        envs["IRC_CHANNEL"],
        callback=on_received,
    )

    irc_client.start()


if __name__ == "__main__":
    main()
