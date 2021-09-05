from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
)
from typing import Optional


def check_spaces(data: str):
    if " " in data:
        raise ValidationError("No space allowed in name or secret")


class AppSchema(Schema):
    name = fields.Str(
        validate=[check_spaces, validate.Length(min=5, max=80)], required=True
    )
    secret = fields.Str(
        validate=[check_spaces, validate.Length(min=3, max=80)],
        required=True,
        load_only=True,
    )
