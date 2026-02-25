import uuid
import os
import json
from flask import request,jsonify
from flask.views import MethodView, View
from flask_smorest import Blueprint,abort
from flask import render_template

from app.database.db import db
from app.schema import DocumentCollectionSchema
from app.models import DocumentCollection as DocumentCollectionModel
from app.routes import api
from app.task_queue import task_queue
from app.services.Embedding.process_document import process_document_embedding

from werkzeug.utils import secure_filename

blp = Blueprint(
    "document_collection",
    __name__,
    url_prefix="/document-collections",
    description="Document Collection operations"
)

@blp.route("/<string:document_id>")
class DocumentCollection(MethodView):

    def get (self, document_id):
        return {"message": f"Welcome to RAG POC document {document_id}", "status": 200}

    def delete(self):
        pass

@blp.route("")
class DocumentCollectionList(MethodView):

    @blp.response(200, DocumentCollectionSchema(many=True))
    def get(self):
        return DocumentCollectionModel.query.all()


    # @blp.arguments(DocumentSchema)
    # @blp.response(201, DocumentSchema)

    def post(self):
        
        pass

    
@blp.route("/embedding/<string:collection_id>")
def get_document_embedding_by_collection_id(collection_id):
    print(f"EMBEDDINGS: ${collection_id}")

    data = DocumentCollectionModel.query.filter_by(uuid=collection_id).all()


    return [item.to_dict() for item in data], 200
