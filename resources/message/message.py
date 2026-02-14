import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint("message", __name__, description="Operations on message")


@blp.route("/message/<string:message_id>")

class Message(MethodView):
    
    def get (self, message_id):

        return {"message": f"Welcome to RAG POC message {message_id}", "status": 200}


    def delete(self):
        pass