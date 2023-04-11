import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Flask, render_template

sys.path.append(str(Path(__file__).resolve().parent.parent))

from snapper.tracker import track
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


if __name__ == "__main__":
    envs = get_envs()
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL")
        if os.getenv("LOG_LEVEL") != ""
        else envs["LOG_LEVEL"],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    executor = ThreadPoolExecutor(1)
    #    executor.submit(track)
    app.run(port=8080)
