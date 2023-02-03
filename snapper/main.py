import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))


from dotenv import dotenv_values

from util import get_project_root


def main() -> None:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.debug("This is main!")
    env_variables = dotenv_values(get_project_root() / ".env")
    logger.debug(f'IRC OAUTH: {env_variables["IRC_OAUTH"]}')


if __name__ == "__main__":
    main()
