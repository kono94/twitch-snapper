import asyncio
import json
import logging
import sys
from pathlib import Path
from threading import Thread
from typing import Any

import aiofiles  # type: ignore
from dotenv import dotenv_values
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
ENVS: dict[str, Any] = dotenv_values(PROJECT_ROOT / ".env")
sys.path.append(str(PROJECT_ROOT))

Log = logging.getLogger(__name__)


async def _init_twitchAPI() -> Twitch:
    twitch = await Twitch(
        ENVS["TWITCH_APP_ID"],
        ENVS["TWITCH_APP_SECRET"],
    )
    Log.debug("Logged into twitch")

    target_scope = [AuthScope.CLIPS_EDIT]
    token = ENVS["TWITCH_CLIENT_TOKEN"]
    refresh_token = ENVS["TWITCH_CLIENT_REFRESH_TOKEN"]
    await twitch.set_user_authentication(token, target_scope, refresh_token)
    Log.debug("Set User Authentication")
    return twitch


async def _main():
    from snapper.database import Stream, get_all
    from snapper.observer import StreamObserver

    twitchAPI: Twitch = await _init_twitchAPI()
    for stream in await get_all(Stream):
        try:
            oberserver = StreamObserver(twitchAPI, stream)
            # await oberserver.start_observing()
        except AssertionError as e:
            Log.error(e)


# stop_event = asyncio.Event()  # Create an asyncio.Event
# await stop_event.wait()  # This will block the main coroutine indefinitely


async def read_test_channel_file_async() -> list:
    async with aiofiles.open("test_channels.json", mode="r") as f:
        content = await f.read()
        test_channels = json.loads(content)
    return test_channels


if __name__ == "__main__":
    logging.basicConfig(
        level=ENVS["LOG_LEVEL"],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from snapper.app import app

    loop = asyncio.new_event_loop()
    loop.run_until_complete(_main())
    app.run(port=8088, debug=True, use_reloader=True, loop=loop)
