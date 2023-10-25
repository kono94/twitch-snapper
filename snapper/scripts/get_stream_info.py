import asyncio
import sys

from twitchAPI.helper import first
from twitchAPI.object import TwitchUser

from snapper.config import configure_environment
from snapper.twitch import TwitchApiHandler


async def main(channel_name: str):
    twitch = await TwitchApiHandler.init_twitchAPI()
    user: TwitchUser | None = await first(twitch.get_users(logins=[channel_name]))
    print(vars(user))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a channel name.")
        sys.exit(1)

    configure_environment(".env")
    asyncio.run(main(sys.argv[1]))
