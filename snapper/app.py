from flask import Flask, render_template

from snapper.main import PROJECT_ROOT

app = Flask(
    __name__,
    template_folder=PROJECT_ROOT / "frontend/templates",
    static_folder=PROJECT_ROOT / "frontend/static",
)


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
