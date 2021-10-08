from marshmallow import (
    Schema,
    fields,
    validate,
)

from store.schemas import StoreSchema


class PetSchema(Schema):
    uid = fields.Str(dump_only=True)
    name = fields.Str(validate=[validate.Length(min=1, max=60)], required=True)
    species = fields.Str(
        validate=[validate.Length(min=1, max=60)], required=True
    )
    breed = fields.Str(validate=[validate.Length(min=1, max=60)], required=True)
    age = fields.Int()
    store_uid = fields.Str(load_only=True, required=True)
    store = fields.Nested(StoreSchema, dump_only=True)
    price = (fields.Float(),)
    sold = fields.Boolean()
    received_date = fields.DateTime()
    sold_date = fields.DateTime()
    live = fields.Boolean(required=False)
