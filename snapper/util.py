import logging
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_envs() -> dict[str, Any]:
    return dotenv_values(get_project_root() / ".env")
