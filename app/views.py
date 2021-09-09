from quart.views import MethodView
from quart import current_app, request, jsonify
from passlib.hash import pbkdf2_sha256
import uuid
from datetime import datetime, timedelta

from app.models import app_table, app_access_table
from .schemas import AppSchema
from utils.json_parser import get_json_payload
from utils.api_responses import success, fail


class AppAPI(MethodView):
    async def post(self):
        conn = current_app.dbc  # typing: ignore

        app_schema = AppSchema()
        json_data = await get_json_payload(request, app_schema)

        # check is app exists
        app_query = app_table.select().where(
            app_table.c.name == json_data["app_id"]
        )
        existing_app = await conn.fetch_one(query=app_query)

        if existing_app:
            error_code = "APP_ID_ALREADY_EXISTS"
            return fail(error_code=error_code), 400
        else:
            # create the credentials
            hash: str = pbkdf2_sha256.hash(json_data["app_secret"])
            app_insert = app_table.insert().values(
                name=json_data["app_id"], secret=hash
            )
            await conn.execute(query=app_insert)

        return success({}), 201


class AccessAPI(MethodView):
    async def post(self):
        conn = current_app.dbc  # typing: ignore

        app_schema = AppSchema()
        json_data = await get_json_payload(request, app_schema)

        app_query = app_table.select().where(
            app_table.c.name == json_data["app_id"]
        )
        app = await conn.fetch_one(query=app_query)

        if not app:
            error_code = "INCORRECT_CREDENTIALS"
            return fail(error_code=error_code), 403
        else:
            # generate a token
            if pbkdf2_sha256.verify(json_data["app_secret"], app.get("secret")):
                # delete existing tokens
                stmt = app_access_table.delete().where(
                    app_access_table.c.app_id == app.get("id")
                )
                result = await conn.execute(stmt)

                # set the token
                token = str(uuid.uuid4())
                now = datetime.utcnow().replace(second=0, microsecond=0)
                expires = now + timedelta(days=30)

                # insert access token in db
                access_insert = app_access_table.insert().values(
                    app_id=app["id"], token=token, expires=expires
                )
                result = await conn.execute(query=access_insert)

                # convert satetime to ISO
                expires_3339 = expires.isoformat("T") + "Z"

                return success({"token": token, "expires": expires_3339}), 200
            else:
                error_code = "INCORRECT_CREDENTIALS"
                return fail(error_code=error_code), 403
