import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from snapper.chat.irc import IRC
from util import get_envs


def main() -> None:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.debug("This is main!")
    envs = get_envs()
    logger.debug(f'IRC OAUTH: {envs["IRC_OAUTH"]}')
    irc = IRC(nickname=envs["IRC_NICKNAME"], password=envs["IRC_OAUTH"], channel=envs["IRC_CHANNEL"])
    irc.start()


if __name__ == "__main__":
    main()
