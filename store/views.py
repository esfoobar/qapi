from quart.views import MethodView
from quart import current_app, request
import uuid
from typing import Optional

from .models import store_table
from .schemas import StoreSchema
from utils.json_parser import get_json_payload
from utils.api_responses import success, fail


class StoreAPI(MethodView):
    # def __init__(self):
    #     self.STORES_PER_PAGE = 10
    #     self.PETS_PER_PAGE = 10
    #     if (
    #         request.method != "GET" and request.method != "DELETE"
    #     ) and not request.json:
    #         return fail, 400

    # async def get(self, store_id):
    #     if store_id:
    #         store = await StoreAPI._get_store(uid=store_id)
    #         if store:
    #             response = {
    #                 "store": store,
    #                 "links": StoreAPI().get_self_url(store),
    #             }
    #             return success(response), 201
    #         else:
    #             return {}, 404
    # else:
    #     page = int(request.args.get("page", 1))
    #     stores_query = (
    #         store_table.select()
    #         .where(store_table.c.live == True)
    #         .offset(page - 1)
    #         .limit(self.STORES_PER_PAGE)
    #     )

    #     response = {
    #         "result": "ok",
    #         "links": [{"href": "/stores/?page=%s" % page, "rel": "self"}],
    #         "stores": stores_obj(stores),
    #     }
    #     if stores.has_prev:
    #         response["links"].append(
    #             {
    #                 "href": "/stores/?page=%s" % (stores.prev_num),
    #                 "rel": "previous",
    #             }
    #         )
    #     if stores.has_next:
    #         response["links"].append(
    #             {
    #                 "href": "/stores/?page=%s" % (stores.next_num),
    #                 "rel": "next",
    #             }
    #         )
    #     return jsonify(response), 200

    async def post(self):
        conn = current_app.dbc  # typing: ignore

        store_schema = StoreSchema()
        json_data = await get_json_payload(request, store_schema)

        # store in the database
        json_data["uid"] = str(uuid.uuid4())
        store_insert = store_table.insert().values(dict(json_data))
        await conn.execute(query=store_insert)

        # get from database
        store_obj = await StoreAPI._get_store(uid=json_data["uid"])
        response = {
            "store": store_obj,
            "links": StoreAPI().get_self_url(store_obj),
        }
        return success(response), 201

    @staticmethod
    async def _get_store(uid: str) -> Optional[dict]:
        conn = current_app.dbc  # typing: ignore

        store_query = store_table.select().where(
            (store_table.c.uid == uid) & (store_table.c.live == True)
        )
        store_record = await conn.fetch_one(query=store_query)

        if not store_record:
            return None

        store_obj = StoreSchema().dump(dict(store_record))
        return store_obj

    @staticmethod
    def get_self_url(obj):
        uid = obj["uid"]
        return [{"href": f"/store/{ uid }", "rel": "self"}]
