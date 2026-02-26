from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.database.db import db
from app.schema.message import MessageSchema
from app.models import Message as MessageModel

from app.services.Message import AIMessageService
from app.routes import api
from flask import current_app


blp = Blueprint(
    "messages",
    __name__,
    url_prefix="/messages",
    description="Message operations"
)

@blp.route("/<string:message_id>")
class Message(MethodView):

    def get (self, message_id):
        return {"message": f"Welcome to RAG POC message {message_id}", "status": 200}


    def delete(self):
        pass

@blp.route("")
class MessageList(MethodView):

    @blp.response(200, MessageSchema(many=True))
    def get(self):

        return MessageModel.query.all()

    @blp.arguments(MessageSchema)
    # @blp.response(201, MessageSchema)
    def post(self, message_data):


        # message_data = request.get_json()
        input_text = message_data["content"]
        session_id = message_data["conversation_id"]

        
        try:
            # save USER message first
            user_message = MessageModel(**message_data)
            db.session.add(user_message)

            # generate AI response
            ai_text = current_app.ai_service.ask(session_id, input_text)

            print(f"AI RESPONSE: {ai_text}")

            ai_message_data = {
                "content": ai_text["answer"],
                "conversation_id": session_id,
                "role": "ai"
            }

            ai_message = MessageModel(**ai_message_data)
            db.session.add(ai_message)

            # commit once (atomic)
            db.session.commit()

            return {
                "user": message_data,
                "ai": ai_message_data
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))



        return {"user": message_data, "ai": ai_message_data}


@blp.route("/conversation/<string:conversation_id>")
def get_messages_by_conversation_id(conversation_id):
    data = MessageModel.query.filter_by(conversation_id=conversation_id).all()
    return [item.to_dict() for item in data], 200