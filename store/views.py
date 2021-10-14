from quart.views import MethodView
from quart import current_app, request
import uuid
from typing import Optional
from sqlalchemy import select

from .models import store_table
from .schemas import StoreSchema
from utils.json_parser import get_json_payload
from utils.api_responses import success
from app.decorators import app_required
from utils.paginate import paginate


class StoreAPI(MethodView):

    decorators = [app_required]

    def __init__(self):
        self.STORES_PER_PAGE = 10

    async def get(self, store_uid):
        if store_uid:
            store = await StoreAPI._get_store(uid=store_uid)
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
            stores_query = select(store_table).where(store_table.c.live == True)
            stores_paginate = await paginate(
                conn, stores_query, page, self.STORES_PER_PAGE
            )
            stores_records = stores_paginate.items
            stores_schema = StoreSchema(many=True)
            stores_list = stores_schema.dump(stores_records)

            response = {
                "stores": stores_list,
            }

            response["links"] = [
                {"href": f"/stores/?page={page}", "rel": "self"}
            ]

            if stores_paginate.has_previous:
                response["links"].append(
                    {
                        "href": f"/stores/?page={stores_paginate.previous_page}",
                        "rel": "previous",
                    }
                )

            if stores_paginate.has_next:
                response["links"].append(
                    {
                        "href": f"/stores/?page={stores_paginate.next_page}",
                        "rel": "next",
                    }
                )

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
        store_obj = await StoreAPI._get_store(uid=json_data["uid"])
        response = {
            "store": store_obj,
            "links": StoreAPI().get_self_url(store_obj),
        }
        return success(response), 201

    async def put(self, store_uid):
        conn = current_app.dbc  # type: ignore

        store = await StoreAPI._get_store(uid=store_uid)
        if not store:
            return {}, 404

        store_schema = StoreSchema()
        json_data = await get_json_payload(request, store_schema)

        store_update = store_table.update(
            store_table.c.uid == store["uid"]
        ).values(json_data)
        await conn.execute(query=store_update)

        # get from database
        store_obj = await StoreAPI._get_store(uid=store["uid"])
        response = {
            "store": store_obj,
            "links": StoreAPI().get_self_url(store_obj),
        }
        return success(response), 200

    async def delete(self, store_uid):
        conn = current_app.dbc  # type: ignore

        store = await StoreAPI._get_store(uid=store_uid)
        if not store:
            return {}, 404

        store["live"] = False

        store_update = store_table.update(
            store_table.c.uid == store["uid"]
        ).values(store)
        await conn.execute(query=store_update)

        # get from database
        store_obj = await StoreAPI._get_store(uid=store["uid"])
        response = {}
        return success(response), 200

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
