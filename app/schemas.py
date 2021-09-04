from marshmallow import Schema, fields


class AppSchema(Schema):
    name = fields.Str(required=True)
    secret = fields.Str(required=True)
