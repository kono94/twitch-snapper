import logging
import os
from enum import Enum

Log = logging.getLogger(__name__)


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


def get_env_variable(var_name: str):
    var_value = os.getenv(var_name)
    if var_value is None:
        raise EnvironmentError(f"Environment variable {var_name} is not set")
    return var_value
