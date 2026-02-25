from app.database.db import db
import uuid
from datetime import datetime

class DocumentCollection(db.Model):
    __tablename__ = "langchain_pg_collection"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String)
    cmetadata = db.Column(db.Text)


    def to_dict(self):
        return {"uuid": self.uuid, "name": self.name}