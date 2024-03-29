import asyncio
import logging
import sys

from hypercorn.asyncio import serve
from hypercorn.config import Config
from twitchAPI.twitch import Twitch

from snapper.app import app
from snapper.config import configure_environment, configure_logging, get_env_variable
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

    loop = asyncio.get_event_loop()

    if len(sys.argv) < 2:
        Log.info("Observing streams, possibly creating new clips")
        loop.run_until_complete(_main())
    else:
        Log.info("Not observing stream, just serving frontend")

    prod_mode = get_env_variable("APP_ENV").lower() == "prod"
    host = get_env_variable("APP_HOST")
    port = int(get_env_variable("APP_PORT"))

    if prod_mode:
        Log.info("Starting in production mode and using hypercorn ASGI server")
        config = Config()
        config.bind = [host + ":" + str(port)]
        loop.run_until_complete(serve(app, config))
    else:
        Log.info("Starting in dev/test mode and using debug mode of Quart app")
        app.run(host=host, port=port, debug=True, use_reloader=True, loop=loop)
