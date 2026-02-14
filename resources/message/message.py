import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from services.LLM import LLMModel
from services.Prompt import Prompt
from langchain_core.output_parsers import StrOutputParser
from schema.message import MessageSchema

blp = Blueprint("message", __name__, description="Operations on message")


@blp.route("/message/<string:message_id>")
class Message(MethodView):

    def get (self, message_id):
        return {"message": f"Welcome to RAG POC message {message_id}", "status": 200}


    def delete(self):
        pass

@blp.route("/message")
class MessageList(MethodView):
    def get(self):
        pass

    @blp.arguments(MessageSchema)
    def post(self, message_data):

        llm = LLMModel().get()
        prompt = Prompt().get()
        output_parser = StrOutputParser()    

        chain = prompt|llm|output_parser

        input_text = message_data["message"]

        return {"response": chain.invoke({"question": input_text})}