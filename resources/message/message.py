import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from services.LLM import LLMModel
from services.Prompt import Prompt
from langchain_core.output_parsers import StrOutputParser

from sqlalchemy.exc import SQLAlchemyError

from db import db
from schema.message import MessageSchema
from models import MessageModel
blp = Blueprint("message", __name__, description="Operations on message")


@blp.route("/message/<string:message_id>")
class Message(MethodView):

    def get (self, message_id):
        return {"message": f"Welcome to RAG POC message {message_id}", "status": 200}


    def delete(self):
        pass

@blp.route("/message")
class MessageList(MethodView):

    @blp.response(200, MessageSchema(many=True))
    def get(self):

        return MessageModel.query.all()

    @blp.arguments(MessageSchema)
    @blp.response(201, MessageSchema)
    def post(self, message_data):

        # llm = LLMModel().get()
        # prompt = Prompt().get()
        # output_parser = StrOutputParser()    

        # chain = prompt|llm|output_parser

        # input_text = message_data["message"]

        message = MessageModel(**message_data)

        try:
            db.session.add(message)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the item.")


        # return {"response": chain.invoke({"question": input_text})}

        return message