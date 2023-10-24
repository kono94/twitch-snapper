import asyncio
import sys
from pathlib import Path

from twitchAPI.helper import first
from twitchAPI.object import TwitchUser

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from snapper.main import _init_twitchAPI


async def main(channel_name: str):
    twitch = await _init_twitchAPI()
    user: TwitchUser | None = await first(twitch.get_users(logins=[channel_name]))
    print(vars(user))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a channel name.")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
