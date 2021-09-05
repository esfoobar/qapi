from quart.views import MethodView
from quart import request, abort, jsonify
from passlib.hash import pbkdf2_sha256
import uuid
from datetime import datetime, timedelta

from app.models import app_table, app_access_table
from .schemas import AppSchema
from utils.quartparser import get_json_payload


class AppAPI(MethodView):
    async def post(self):
        app_schema = AppSchema()
        json_data = await get_json_payload(request, app_schema)
        pass

        # existing_app = App.objects.filter(
        #     app_id=request.json.get("app_id")
        # ).first()

        # check is app exists
        # app_query = app_table.select().where(app_table.c.name == json_data)
        # user_row = await conn.fetch_one(query=user_query)

        # if existing_app:
        #     error = {"code": "APP_ID_ALREADY_EXISTS"}
        #     return jsonify({"error": error}), 400
        # else:
        # create the credentials
        # salt = bcrypt.gensalt()
        # hashed_password = bcrypt.hashpw(
        #     request.json.get("app_secret"), salt
        # )
        # app = App(
        #     app_id=request.json.get("app_id"), app_secret=hashed_password
        # ).save()

        if json_data:
            return jsonify({"result": "ok"})


class AccessAPI(MethodView):
#     def post(self):
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
