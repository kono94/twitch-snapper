import asyncio
import logging
import signal
import sys
from pathlib import Path

from flask import Flask, render_template
from twitchAPI.twitch import Twitch

sys.path.append(str(Path(__file__).resolve().parent.parent))

from snapper.chat.observer import StreamObserver
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


async def main(envs):
    twitchAPI = await Twitch(envs["TWITCH_APP_ID"], envs["TWITCH_APP_SECRET"])
    lck = StreamObserver(twitchAPI)
    await lck.start_observing()


if __name__ == "__main__":
    envs = get_envs()
    logging.basicConfig(
        level=envs["LOG_LEVEL"],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(main(envs))
    loop.run_forever()
    # app.run(port=8080)
