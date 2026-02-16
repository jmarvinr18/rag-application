from marshmallow import Schema, fields

class MessageSchema(Schema):
    id = fields.UUID(dump_only=True)
    conversation_id = fields.Str(required=True)
    content = fields.Str(required=True)
    role = fields.Str(required=True)
    created_at = fields.DateTime()