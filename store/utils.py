from quart import current_app, request
from sqlalchemy import select
from typing import Optional

from .models import store_table
from .schemas import StoreSchema
from utils.paginate import paginate

STORES_PER_PAGE = 10


async def get_store(
    uid: Optional[str] = None, id: Optional[int] = None
) -> Optional[dict]:
    conn = current_app.dbc  # type: ignore

    if uid:
        store_where = store_table.c.uid == uid
    elif id:
        store_where = store_table.c.id == id
    else:
        return None

    store_query = store_table.select().where(
        store_where & (store_table.c.live == True)
    )
    store_record = await conn.fetch_one(query=store_query)

    if not store_record:
        return None

    store_obj = StoreSchema().dump(dict(store_record))
    return store_obj


def get_self_url(obj: StoreSchema):
    uid = obj["uid"]
    return [{"href": f"/stores/{ uid }", "rel": "self"}]


async def get_stores() -> dict:
    conn = current_app.dbc  # type: ignore

    page = int(request.args.get("page", 1))
    stores_query = select(store_table).where(store_table.c.live == True)
    stores_paginate = await paginate(conn, stores_query, page, STORES_PER_PAGE)
    stores_records = stores_paginate.items
    stores_schema = StoreSchema(many=True)
    stores_list = stores_schema.dump(stores_records)

    response = {
        "stores": stores_list,
    }

    response["links"] = [{"href": f"/stores/?page={page}", "rel": "self"}]

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

    return response
