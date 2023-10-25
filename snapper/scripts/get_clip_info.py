import asyncio
import sys

from twitchAPI.helper import first
from twitchAPI.object import Clip as TwitchClip

from snapper.config import configure_environment
from snapper.twitch import TwitchApiHandler


async def main(clip_id: str):
    twitch = await TwitchApiHandler.init_twitchAPI()
    clip: TwitchClip | None = None
    while (clip := await first(twitch.get_clips(clip_id=[clip_id]))) is None:
        await asyncio.sleep(1)

    print(vars(clip))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a clip_id.")
        sys.exit(1)
    configure_environment(".env")
    asyncio.run(main(sys.argv[1]))
