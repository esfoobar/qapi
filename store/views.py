from quart.views import MethodView
from quart import current_app, request
import uuid
from typing import Optional
from sqlalchemy import select

from .models import store_table
from .schemas import StoreSchema
from utils.json_parser import get_json_payload
from utils.api_responses import success, fail
from app.decorators import app_required


class StoreAPI(MethodView):

    decorators = [app_required]

    def __init__(self):
        self.STORES_PER_PAGE = 10

    async def get(self, store_id):
        if store_id:
            store = await StoreAPI._get_store(uid=store_id)
            if store:
                response = {
                    "store": store,
                    "links": StoreAPI().get_self_url(store),
                }
                return success(response), 200
            else:
                return {}, 404
        else:
            conn = current_app.dbc  # type: ignore

            page = int(request.args.get("page", 1))
            stores_query = (
                select(store_table)
                .where(store_table.c.live == True)
                .offset(page - 1)
                .limit(self.STORES_PER_PAGE)
            )
            stores_records = await conn.fetch_all(query=stores_query)
            pass
            # response = {
            #     "result": "ok",
            #     "links": [{"href": "/stores/?page=%s" % page, "rel": "self"}],
            #     "stores": stores_obj(stores),
            # }
            # if stores.has_prev:
            #     response["links"].append(
            #         {
            #             "href": "/stores/?page=%s" % (stores.prev_num),
            #             "rel": "previous",
            #         }
            #     )
            # if stores.has_next:
            #     response["links"].append(
            #         {
            #             "href": "/stores/?page=%s" % (stores.next_num),
            #             "rel": "next",
            #         }
            #     )
            # return jsonify(response), 200

    async def post(self):
        conn = current_app.dbc  # type: ignore

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
        conn = current_app.dbc  # type: ignore

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
        return [{"href": f"/stores/{ uid }", "rel": "self"}]
