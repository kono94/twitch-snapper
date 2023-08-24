import asyncio
import logging
import sys
from pathlib import Path
from threading import Thread

from flask import Flask, render_template
from twitchAPI.helper import first
from twitchAPI.object import TwitchUser
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope

sys.path.append(str(Path(__file__).resolve().parent.parent))

from snapper.database import Stream, get_all, persist
from snapper.observer import StreamObserver
from snapper.util import get_envs, get_project_root

app = Flask(
    __name__,
    template_folder=get_project_root() / "frontend/templates",
    static_folder=get_project_root() / "frontend/static",
)

Log = logging.getLogger(__name__)


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/clips")
def clips():
    clips = [{"title": f"Clip #{id}"} for id in range(0, 5)]
    return render_template("clips.html", clips=clips)


@app.route("/about")
def about():
    return render_template("about.html")


async def init_twitchAPI() -> Twitch:
    envs = get_envs()
    twitch = await Twitch(
        envs["TWITCH_APP_ID"],
        envs["TWITCH_APP_SECRET"],
    )
    Log.debug("Logged into twitch")
    target_scope = [AuthScope.CLIPS_EDIT]

    token = envs["TWITCH_CLIENT_TOKEN"]
    refresh_token = envs["TWITCH_CLIENT_REFRESH_TOKEN"]
    await twitch.set_user_authentication(token, target_scope, refresh_token)
    Log.debug("Set User Authentication")

    return twitch


async def create_stream(twitchAPI, channel_name, keyword_list, **kwargs):
    user_info: TwitchUser | None = await first(
        twitchAPI.get_users(logins=[channel_name])
    )
    if not user_info:
        raise Exception(f"Cannot extract broadcast_id for channel {channel_name}.")
    stream = Stream(
        channel_name=channel_name,
        broadcaster_id=user_info.id,
        keyword_list=keyword_list,
        min_trigger_interval=10,
        **kwargs,
    )
    return stream


async def dev_setup(twitchAPI):
    from snapper.database import drop_and_create_db

    await drop_and_create_db()
    new_stream = await create_stream(
        twitchAPI, "tarik", ["KEK", "OWO", "LUL"], trigger_threshold=5
    )
    await persist(new_stream)


async def main():
    twitchAPI = await init_twitchAPI()

    if envs["APP_ENV"] == "dev":
        await dev_setup(twitchAPI)

    for stream in await get_all(Stream):
        try:
            a = StreamObserver(twitchAPI, stream)
            await a.start_observing()
        except AssertionError as e:
            Log.error(e)

    stop_event = asyncio.Event()  # Create an asyncio.Event
    await stop_event.wait()  # This will block the main coroutine indefinitely


if __name__ == "__main__":
    envs = get_envs()

    logging.basicConfig(
        level=envs["LOG_LEVEL"],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def run_flask_app():
        app.run(port=8088)

    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    asyncio.run(main())
