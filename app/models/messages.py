import uuid
from datetime import datetime
from app.database.db import db

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    conversation_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("conversations.id", ondelete="CASCADE")
    )

    role = db.Column(db.Text)  # user | assistant | system
    content = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    conversation = db.relationship("Conversation", back_populates="messages")

    def to_dict(self):
        return {"id": self.id, 
                "conversation_id": self.conversation_id,
                "role": self.role,
                "content": self.content,
                "created_at": self.created_at
                }    