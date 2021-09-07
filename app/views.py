from quart.views import MethodView
from quart import current_app, request, jsonify
from passlib.hash import pbkdf2_sha256
import uuid
from datetime import datetime, timedelta

from sqlalchemy.sql.expression import select

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
            app_table.c.name == json_data["name"]
        )
        existing_app = await conn.fetch_one(query=app_query)

        if existing_app:
            error_code = "APP_ID_ALREADY_EXISTS"
            return fail(error_code=error_code), 400
        else:
            # create the credentials
            hash: str = pbkdf2_sha256.hash(json_data["secret"])
            app_insert = app_table.insert().values(
                name=json_data["name"], secret=hash
            )
            await conn.execute(query=app_insert)

        return success({}), 201


class AccessAPI(MethodView):
    def post(self):
        pass


#         if not "app_id" in request.json or not "app_secret" in request.json:
#             error = {"code": "MISSING_APP_ID_OR_APP_SECRET"}
#             return jsonify({"error": error}), 400

#         app = App.objects.filter(app_id=request.json.get("app_id")).first()
#         if not app:
#             error = {"code": "INCORRECT_CREDENTIALS"}
#             return jsonify({"error": error}), 403
#         else:
#             # generate a token
#             if (
#                 bcrypt.hashpw(request.json.get("app_secret"), app.app_secret)
#                 == app.app_secret
#             ):
#                 # delete existing tokens
#                 existing_tokens = Access.objects.filter(app=app).delete()
#                 token = str(uuid.uuid4())
#                 now = datetime.utcnow().replace(second=0, microsecond=0)
#                 expires = now + timedelta(days=30)
#                 access = Access(app=app, token=token, expires=expires).save()
#                 expires_3339 = expires.isoformat("T") + "Z"
#                 return jsonify({"token": token, "expires": expires_3339}), 200
#             else:
#                 error = {"code": "INCORRECT_CREDENTIALS"}
#                 return jsonify({"error": error}), 403
