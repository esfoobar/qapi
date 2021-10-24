from quart import request, current_app
from typing import Optional
from quart.views import MethodView
import uuid
from sqlalchemy import select

from app.decorators import app_required
from .models import pet_table
from .schemas import PetSchema
from .utils import get_pet, get_pets, get_self_url
from utils.json_parser import get_json_payload
from utils.api_responses import success, fail
from store.models import store_table


class PetAPI(MethodView):

    decorators = [app_required]

    def __init__(self):
        self.PETS_PER_PAGE = 10

    async def get(self, pet_uid):
        if pet_uid:
            pet_obj = await get_pet(uid=pet_uid)
            if pet_obj:
                response = {
                    "pet": pet_obj,
                    "links": get_self_url(pet_obj),
                }
                return success(response), 200
            else:
                return {}, 404
        else:
            response = await get_pets()
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
        pet_obj = await get_pet(uid=json_data["uid"])
        response = {
            "pet": pet_obj,
            "links": get_self_url(pet_obj),
        }
        return success(response), 201

    async def put(self, pet_uid):
        conn = current_app.dbc  # type: ignore

        pet_obj = await get_pet(uid=pet_uid)
        if not pet_obj:
            return {}, 404

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

        pet_update = pet_table.update(pet_table.c.uid == pet_obj["uid"]).values(
            json_data
        )
        await conn.execute(query=pet_update)

        # get from database
        pet_obj = await get_pet(uid=pet_obj["uid"])
        response = {
            "pet": pet_obj,
            "links": get_self_url(pet_obj),
        }
        return success(response), 200

    async def delete(self, pet_uid):
        conn = current_app.dbc  # type: ignore

        pet_obj = await get_pet(uid=pet_uid)
        if not pet_obj:
            return {}, 404

        pet_update = pet_table.update(pet_table.c.uid == pet_obj["uid"]).values(
            live=False
        )
        await conn.execute(query=pet_update)

        # get from database
        response = {}
        return success(response), 200
