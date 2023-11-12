import logging
from datetime import datetime

from quart import Quart, jsonify, render_template, request
from sqlalchemy import desc

from snapper.database import Clip, TransactionHandler
from snapper.dto import StreamActiveUpdate
from snapper.exception import NotFoundException

app: Quart = Quart(
    __name__,
    template_folder="frontend/templates/",
    static_folder="frontend/static/",
)

#########################
###       PAGES       ###
#########################


@app.route("/home")
async def home():
    return await render_template("index.html")


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/clips")
async def clips():
    return await render_template("clips.html")


@app.route("/streams")
async def streams():
    return await render_template("streams.html")


@app.route("/about")
async def about():
    return await render_template("about.html")


#########################
###       API         ###
#########################


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


@app.route("/api/streams", methods=["GET"])
async def api_streams():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    sort_by = request.args.get("sort_by", "latest")

    order_by_clip_count = True if sort_by == "clip_count" else False
    streams = await TransactionHandler.get_streams_with_clip_count(
        page, per_page, order_by_clip_count
    )

    json_data = [
        {
            **streamInfo.stream.to_dict(),
            "clip_count": streamInfo.clip_count,
            "keywords": [keyword.to_dict() for keyword in streamInfo.stream.keywords],
        }
        for streamInfo in streams
    ]
    return jsonify(json_data)


@app.before_serving
async def startup():
    logging.getLogger("quart.app").setLevel(logging.DEBUG)


@app.put("/api/stream/<int:stream_id>/active")
async def toggle_stream_active(stream_id: int):
    data = await request.json
    active_update = StreamActiveUpdate(**data)
    return await TransactionHandler.toogle_stream_activeness(
        stream_id, active_update.is_active
    )


@app.errorhandler(NotFoundException)
async def handle_not_found_error(e):
    return {"error": str(e)}, 404
