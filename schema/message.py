from marshmallow import Schema, fields

class MessageSchema(Schema):
    id = fields.Str(dump_only=True)
    message = fields.Str(required=True)