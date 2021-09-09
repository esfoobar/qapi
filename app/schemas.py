from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
)


def check_spaces(data: str):
    if " " in data:
        raise ValidationError("No space allowed")


class AppSchema(Schema):
    app_id = fields.Str(
        validate=[check_spaces, validate.Length(min=5, max=80)], required=True
    )
    app_secret = fields.Str(
        validate=[check_spaces, validate.Length(min=3, max=80)],
        required=True,
        load_only=True,
    )
