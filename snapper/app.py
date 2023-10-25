from datetime import datetime

from quart import Quart, jsonify, render_template, request
from sqlalchemy import asc, desc

from snapper.database import Clip, TransactionHandler

app: Quart = Quart(
    __name__,
    template_folder="frontend/templates/",
    static_folder="frontend/static/",
)


@app.route("/home")
async def home():
    return await render_template("index.html")


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/clips")
async def clips():
    clips = await TransactionHandler.get_all(Clip)
    return await render_template("clips.html", clips=clips)


@app.route("/api/clips", methods=["GET"])
async def api_clips():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    sort_by = request.args.get("sort_by", "latest")
    last_timestamp_iso: str | None = request.args.get("last_timestamp_iso", None)

    if last_timestamp_iso != None:
        print(last_timestamp_iso)
        utc_timestamp = datetime.fromisoformat(
            last_timestamp_iso
        )  # Convert the string to a datetime object
    else:
        utc_timestamp = None

    # Determine sort order
    if sort_by == "latest":
        order_by = desc(Clip.created)
    elif sort_by == "keyword_count":
        order_by = desc(Clip.keyword_count)
    else:
        order_by = desc(Clip.created)  # Default sort

    # Fetch and sort clips from the database, skipping the clips for previous pages
    clips = await TransactionHandler.get_by_page_and_sort(
        Clip, page, per_page, order_by, utc_timestamp
    )

    return jsonify([clip.to_dict() for clip in clips])


@app.route("/about")
async def about():
    return await render_template("about.html")
