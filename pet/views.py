from quart.views import MethodView

from app.decorators import app_required


class PetAPI(MethodView):

    decorators = [app_required]

    async def post(self):
        conn = current_app.dbc  # type: ignore

        pet_schema = PetSchema()
        json_data = await get_json_payload(request, store_schema)

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

    async def _get_pet(uid: str) -> Optional[dict]:
        conn = current_app.dbc  # type: ignore

        pet_query = pet_table.select().where(
            (pet_table.c.uid == uid) & (pet_table.c.live == True)
        )
        pet_record = await conn.fetch_one(query=pet_query)

        if not pet_record:
            return None

        pet_obj = PetSchema().dump(dict(pet_record))
        return pet_obj

    @staticmethod
    def get_self_url(obj):
        uid = obj["uid"]
        return [{"href": f"/pets/{ uid }", "rel": "self"}]
