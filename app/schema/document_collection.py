from marshmallow import Schema, fields

class DocumentCollectionSchema(Schema):
    id = fields.UUID()
    name = fields.Str(required=True)
    cmetadata = fields.Dict()