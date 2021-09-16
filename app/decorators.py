from functools import wraps
from quart import request, jsonify, current_app
import datetime

from app.models import app_table, app_access_table


def app_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        app_id = request.headers.get("X-APP-ID")
        app_token = request.headers.get("X-APP-TOKEN")
        conn = current_app.dbc  # type: ignore

        if app_id is None or app_token is None:
            return jsonify({}), 403

        app_query = app_table.select().where(app_table.c.name == app_id)
        app_record = await conn.fetch_one(query=app_query)
        if not app_record:
            return jsonify({}), 403

        access_query = app_access_table.select().where(
            app_access_table.c.app_id == app_record["id"]
        )
        access_record = await conn.fetch_one(query=access_query)
        if not access_record:
            return jsonify({}), 403
        if access_record["token"] != app_token:
            return jsonify({}), 403
        if access_record["expires"] < datetime.datetime.now(
            datetime.timezone.utc
        ):  # per https://stackoverflow.com/a/24666683
            return jsonify({"error": "TOKEN_EXPIRED"}), 403

        return f(*args, **kwargs)

    return decorated_function
