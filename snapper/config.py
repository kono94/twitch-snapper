import logging
from pathlib import Path

from dotenv import load_dotenv

from snapper.util import get_env_variable

Log = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig(
        level=get_env_variable("LOG_LEVEL"),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def configure_environment(env_file: str = ".env"):
    script_location = Path(__file__).resolve().parent
    dotenv_path = script_location.parent / env_file
    print(
        f"Loading environment variables; Successful={load_dotenv(dotenv_path=dotenv_path)}"
    )
