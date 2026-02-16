import uuid
from datetime import datetime
from app.database.db import db
from pgvector.sqlalchemy import Vector

EMBEDDING_DIM = 384

class DocumentChunk(db.Model):
    __tablename__ = "document_chunks"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("documents.id", ondelete="CASCADE")
    )

    chunk_index = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False)

    embedding = db.Column(Vector(EMBEDDING_DIM))

    token_count = db.Column(db.Integer)
    meta = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    document = db.relationship("Document", back_populates="chunks")
