import uuid
import shortuuid 
from datetime import datetime
from app.database.db import db

class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = db.Column(db.String(22), unique=True, nullable=False, default=shortuuid.uuid)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
