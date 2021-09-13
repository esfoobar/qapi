from quart.views import MethodView
from quart import current_app, request
import uuid

from .models import store_table
from .schemas import StoreSchema
from utils.json_parser import get_json_payload
from utils.api_responses import success


class StoreAPI(MethodView):
    async def post(self):
        conn = current_app.dbc  # typing: ignore

        store_schema = StoreSchema()
        json_data = await get_json_payload(request, store_schema)

        # store in the database
        json_data["uid"]: str = str(uuid.uuid4())
        store_insert = store_table.insert().values(dict(json_data))
        await conn.execute(query=store_insert)

        store_json = {"store": json_data}
        links_json = [{"href": f"/store/{ json_data['uid'] }", "rel": "self"}]

        response = {"store": json_data, "_links": links_json}
        return success(response), 201
