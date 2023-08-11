import logging
from enum import Enum
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_envs() -> dict[str, Any]:
    return dotenv_values(get_project_root() / ".env")


class Color(Enum):
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"


def colored_string(msg: str, color: Color) -> str:
    reset = "\x1b[0m"
    return color.value + msg + reset


def clip_to_string(clip_instance):
    # Create a list of key-value pairs as strings
    attributes_str = [
        f"{attr}: {value}" for attr, value in clip_instance.__dict__.items()
    ]
    # Join the list into a single formatted string
    return "\n".join(attributes_str)
