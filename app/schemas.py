from marshmallow import Schema, fields


class AppSchema(Schema):
    app_id = fields.Str(required=True)
    app_secret = fields.Str(required=True)
