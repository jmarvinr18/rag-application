from marshmallow import Schema, fields

class DocumentChunkSchema(Schema):
    id = fields.UUID()
    document_id = fields.Str(required=True)
    chunk_index = fields.Integer(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(format=str)
    embedding = fields.List(fields.Float())
    metadata = fields.Dict()
    token_count = fields.Int()