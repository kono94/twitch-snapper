import asyncio
import sys
from pathlib import Path

from twitchAPI.helper import first
from twitchAPI.object import Clip as TwitchClip

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from snapper.main import _init_twitchAPI


async def main(clip_id: str):
    twitch = await _init_twitchAPI()
    clip: TwitchClip | None = None
    while (clip := await first(twitch.get_clips(clip_id=[clip_id]))) is None:
        await asyncio.sleep(1)

    print(vars(clip))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a clip_id.")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
