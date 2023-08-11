import asyncio
import logging
import sys
from pathlib import Path
from threading import Thread

from flask import Flask, render_template
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope

sys.path.append(str(Path(__file__).resolve().parent.parent))

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
    twitch = await Twitch(envs["TWITCH_APP_ID"], envs["TWITCH_APP_SECRET"])
    Log.debug("Logged into twitch")
    target_scope = [AuthScope.CLIPS_EDIT]

    token = envs["TWITCH_CLIENT_TOKEN"]
    refresh_token = envs["TWITCH_CLIENT_REFRESH_TOKEN"]
    await twitch.set_user_authentication(token, target_scope, refresh_token)
    Log.debug("Set User Authentication")

    return twitch


async def main():
    twitchAPI = await init_twitchAPI()
    try:
        lck = StreamObserver(envs["IRC_CHANNEL"], twitchAPI)
        await lck.start_observing()
    except AssertionError as e:
        Log.error(e)
        sys.exit(2)


if __name__ == "__main__":
    envs = get_envs()
    logging.basicConfig(
        level=envs["LOG_LEVEL"],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def run_flask_app():
        app.run(port=8080)

    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    loop.create_task(main())
    loop.run_forever()
