from quart import request, current_app
from sqlalchemy import select
from typing import Optional

from .models import pet_table
from .schemas import PetSchema
from utils.paginate import paginate
from store.utils import get_store

PETS_PER_PAGE = 10


async def get_pet(uid: str) -> Optional[dict]:
    conn = current_app.dbc  # type: ignore

    pet_query = pet_table.select().where(
        (pet_table.c.uid == uid) & (pet_table.c.live == True)
    )
    pet_record = await conn.fetch_one(query=pet_query)

    if not pet_record:
        return None
    else:
        pet_json = dict(pet_record)

    # fetch store data and remove the internal ir
    pet_json["store"] = await get_store(id=pet_record["store_id"])
    del pet_json["store_id"]

    pet_obj = PetSchema().dump(pet_json)
    return pet_obj


def get_self_url(obj: PetSchema):
    uid = obj["uid"]
    return [{"href": f"/pets/{ uid }", "rel": "self"}]


async def get_pets(store_uid: Optional[str] = None) -> dict:
    conn = current_app.dbc  # type: ignore

    pets_query = select(pet_table).where(pet_table.c.live == True)

    page = int(request.args.get("page", 1))
    pets_paginate = await paginate(conn, pets_query, page, PETS_PER_PAGE)
    pets_records = pets_paginate.items
    pets_schema = PetSchema(many=True)
    pets_list = pets_schema.dump(pets_records)

    # load stores
    for pet in pets_list:
        pet["store"] = await get_store(id=pet["store_id"])
        del pet["store_id"]

    response = {
        "pets": pets_list,
    }

    response["links"] = [{"href": f"/pets/?page={page}", "rel": "self"}]

    if pets_paginate.has_previous:
        response["links"].append(
            {
                "href": f"/pets/?page={pets_paginate.previous_page}",
                "rel": "previous",
            }
        )

    if pets_paginate.has_next:
        response["links"].append(
            {
                "href": f"/pets/?page={pets_paginate.next_page}",
                "rel": "next",
            }
        )

    return response
