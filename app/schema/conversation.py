from marshmallow import Schema, fields

class ConversationSchema(Schema):
    id = fields.UUID(dump_only=True)
    session_id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)