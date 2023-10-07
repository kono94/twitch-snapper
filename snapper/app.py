from quart import Quart, render_template

from snapper.database import Clip, Stream, get_all
from snapper.main import PROJECT_ROOT

app: Quart = Quart(
    __name__,
    template_folder=str(PROJECT_ROOT / "snapper/frontend/templates"),
    static_folder=str(PROJECT_ROOT / "snapper/frontend/static"),
)


@app.route("/home")
async def home():
    return await render_template("index.html")


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/clips")
async def clips():
    clips = await get_all(Clip)
    return await render_template("clips.html", clips=clips)


@app.route("/about")
async def about():
    return await render_template("about.html")
