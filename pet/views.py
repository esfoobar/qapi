from quart import request, current_app
from typing import Optional
from quart.views import MethodView
import uuid
from sqlalchemy import select

from app.decorators import app_required
from .models import pet_table
from .schemas import PetSchema
from utils.json_parser import get_json_payload
from utils.api_responses import success, fail
from store.models import store_table
from store.views import StoreAPI
from utils.paginate import paginate


class PetAPI(MethodView):

    decorators = [app_required]

    def __init__(self):
        self.PETS_PER_PAGE = 10

    async def get(self, pet_uid):
        if pet_uid:
            pet_obj = await PetAPI._get_pet(uid=pet_uid)
            if pet_obj:
                response = {
                    "pet": pet_obj,
                    "links": PetAPI().get_self_url(pet_obj),
                }
                return success(response), 201
            else:
                return {}, 404
        else:
            conn = current_app.dbc  # type: ignore

            page = int(request.args.get("page", 1))
            pets_query = select(pet_table).where(pet_table.c.live == True)
            pets_paginate = await paginate(
                conn, pets_query, page, self.PETS_PER_PAGE
            )
            pets_records = pets_paginate.items
            pets_schema = PetSchema(many=True)
            pets_list = pets_schema.dump(pets_records)

            # load stores
            for pet in pets_list:
                pet["store"] = await StoreAPI._get_store(id=pet["store_id"])
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

            return success(response), 200

    async def post(self):
        conn = current_app.dbc  # type: ignore

        pet_schema = PetSchema()
        json_data = await get_json_payload(request, pet_schema)

        # Check if store uid is valid
        store_query = store_table.select().where(
            (store_table.c.uid == json_data.get("store_uid"))
            & (store_table.c.live == True)
        )
        store_record = await conn.fetch_one(query=store_query)
        if not store_record:
            error_code = "STORE_NOT_FOUND"
            return fail(error_code=error_code), 400

        # remove store_uid from json_payload and store id
        del json_data["store_uid"]
        json_data["store_id"] = store_record["id"]

        # store in the database
        json_data["uid"] = str(uuid.uuid4())
        pet_insert = pet_table.insert().values(dict(json_data))
        await conn.execute(query=pet_insert)

        # get from database
        pet_obj = await PetAPI._get_pet(uid=json_data["uid"])
        response = {
            "pet": pet_obj,
            "links": PetAPI().get_self_url(pet_obj),
        }
        return success(response), 201

    @staticmethod
    async def _get_pet(uid: str) -> Optional[dict]:
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
        pet_json["store"] = await StoreAPI._get_store(id=pet_record["store_id"])
        del pet_json["store_id"]

        pet_obj = PetSchema().dump(pet_json)
        return pet_obj

    @staticmethod
    def get_self_url(obj):
        uid = obj["uid"]
        return [{"href": f"/pets/{ uid }", "rel": "self"}]
