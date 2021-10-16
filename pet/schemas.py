from marshmallow import (
    Schema,
    fields,
    validate,
)

from store.schemas import StoreSchema
from store.views import StoreAPI


class PetSchema(Schema):
    uid = fields.Str(dump_only=True)
    name = fields.Str(validate=[validate.Length(min=1, max=60)], required=True)
    species = fields.Str(
        validate=[validate.Length(min=1, max=60)], required=True
    )
    breed = fields.Str(validate=[validate.Length(min=1, max=60)], required=True)
    age = fields.Int()
    store_uid = fields.Str(load_only=True, required=True)
    store = fields.Method("get_store")
    price = fields.Float()
    sold = fields.Boolean()
    received_date = fields.DateTime()
    sold_date = fields.DateTime()
    live = fields.Boolean(required=False)

    async def get_store(self, obj):
        store_obj = await StoreAPI._get_store(id=obj["store_id"])
        return store_obj
