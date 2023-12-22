import asyncio
import logging
import sys

from twitchAPI.twitch import Twitch

from snapper.app import app
from snapper.config import configure_environment, configure_logging
from snapper.database import Stream, TransactionHandler
from snapper.observer import StreamObserver
from snapper.twitch import TwitchApiHandler

Log = logging.getLogger(__name__)


async def _main():
    twitchAPI: Twitch = await TwitchApiHandler.init_twitchAPI()
    for stream in await TransactionHandler.get_all(Stream):
        try:
            oberserver = StreamObserver(twitchAPI, stream)
            await oberserver.start_observing()
        except AssertionError as e:
            Log.error(e)


if __name__ == "__main__":
    configure_environment(".env")
    configure_logging()

    loop = asyncio.new_event_loop()
    if len(sys.argv) < 2:
        Log.info("Observing streams, possibly creating new clips")
        loop.run_until_complete(_main())
    else:
        Log.info("Not observing stream, just serving frontend")

    app.run(host="0.0.0.0", port=8088, debug=True, use_reloader=True, loop=loop)
