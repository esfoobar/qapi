from marshmallow import (
    Schema,
    fields,
    validate,
)


class PetSchema(Schema):
    uid = fields.Str(dump_only=True)
    store_uid = fields.Str(input_only=True)
    live = fields.Boolean(required=False)
