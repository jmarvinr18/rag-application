import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from sqlalchemy.exc import SQLAlchemyError

from app.database.db import db
from app.schema.conversation import ConversationSchema
from app.models import Conversation
from app.routes import api


blp = Blueprint(
    "conversation",
    __name__,
    url_prefix="/conversations",
    description="Message operations"
)

@blp.route("/<string:conversation_id>")
class Convesation(MethodView):

    def get (self, conversation_id):
        return {"message": f"Welcome to RAG POC conversation {conversation_id}", "status": 200}


    def delete(self):
        pass

@blp.route("")
class ConvesationList(MethodView):

    @blp.response(200, ConversationSchema(many=True))
    def get(self):

        return Conversation.query.all()

    @blp.arguments(ConversationSchema)
    @blp.response(201, ConversationSchema)
    def post(self, conversation_data):

        conversation = Conversation(**conversation_data) 

        try:
            db.session.add(conversation)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the item.")

        return conversation