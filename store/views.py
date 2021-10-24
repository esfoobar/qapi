from quart.views import MethodView
from quart import current_app, request
import uuid
from sqlalchemy import select

from .models import store_table
from .schemas import StoreSchema
from .utils import get_store, get_self_url, get_stores
from utils.json_parser import get_json_payload
from utils.api_responses import success
from app.decorators import app_required
from utils.paginate import paginate
from pet.utils import get_pets


class StoreAPI(MethodView):

    decorators = [app_required]

    async def get(self, store_uid):
        if store_uid:
            store_obj = await get_store(uid=store_uid)
            if store_obj:
                if "pets" in request.url:
                    response = await get_pets(store_uid=store_uid)
                else:
                    response = {
                        "store": store_obj,
                        "links": get_self_url(store_obj),
                    }
                return success(response), 200
            else:
                return {}, 404
        else:
            response = await get_stores()
            return success(response), 200

    async def post(self):
        conn = current_app.dbc  # type: ignore

        store_schema = StoreSchema()
        json_data = await get_json_payload(request, store_schema)

        # store in the database
        json_data["uid"] = str(uuid.uuid4())
        store_insert = store_table.insert().values(dict(json_data))
        await conn.execute(query=store_insert)

        # get from database
        store_obj = await get_store(uid=json_data["uid"])
        response = {
            "store": store_obj,
            "links": get_self_url(store_obj),
        }
        return success(response), 201

    async def put(self, store_uid):
        conn = current_app.dbc  # type: ignore

        store_obj = await get_store(uid=store_uid)
        if not store_obj:
            return {}, 404

        store_schema = StoreSchema()
        json_data = await get_json_payload(request, store_schema)

        store_update = store_table.update(
            store_table.c.uid == store_obj["uid"]
        ).values(json_data)
        await conn.execute(query=store_update)

        # get from database
        store_obj = await get_store(uid=store_obj["uid"])
        response = {
            "store": store_obj,
            "links": get_self_url(store_obj),
        }
        return success(response), 200

    async def delete(self, store_uid):
        conn = current_app.dbc  # type: ignore

        store_obj = await get_store(uid=store_uid)
        if not store_obj:
            return {}, 404

        store_update = store_table.update(
            store_table.c.uid == store_obj["uid"]
        ).values(live=False)
        await conn.execute(query=store_update)

        # get from database
        response = {}
        return success(response), 200
