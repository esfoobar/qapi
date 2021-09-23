from marshmallow import (
    Schema,
    fields,
    validate,
)


class StoreSchema(Schema):
    uid = fields.Str(dump_only=True)
    neighborhood = fields.Str(
        validate=[validate.Length(min=3, max=255)],
        required=True,
    )
    street_address = fields.Str(
        validate=[validate.Length(min=3, max=255)],
        required=True,
    )
    city = fields.Str(
        validate=[validate.Length(min=3, max=80)],
        required=True,
    )
    state = fields.Str(
        validate=[validate.Length(equal=2)],
        required=True,
    )
    zip_code = fields.Str(
        validate=[validate.Length(equal=5)],
        required=True,
    )
    phone = fields.Str(
        validate=[validate.Length(min=12, max=20)],
        required=True,
    )
    live = fields.Boolean(required=False)
