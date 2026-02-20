import uuid
import os
from flask import request,jsonify
from flask.views import MethodView, View
from flask_smorest import Blueprint,abort
from sqlalchemy.exc import SQLAlchemyError

from app.database.db import db
from app.schema.document import DocumentSchema
from app.models import Document
from app.routes import api
from werkzeug.utils import secure_filename

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader

blp = Blueprint(
    "document",
    __name__,
    url_prefix="/documents",
    description="Document operations"
)

@blp.route("/<string:document_id>")
class Document(MethodView):

    def get (self, document_id):
        return {"message": f"Welcome to RAG POC document {document_id}", "status": 200}


    def delete(self):
        pass

@blp.route("")
class DocumentList(MethodView):

    @blp.response(200, DocumentSchema(many=True))
    def get(self):

        return Document.query.all()

    

    # @blp.arguments(DocumentSchema)
    # @blp.response(201, DocumentSchema)

    def post(self):
        UPLOAD_FOLDER = "uploads"

        if "source" not in request.files:
            return {"error":  "No file part"}, 400

        title = request.form.get("title")
        file = request.files["source"]

        fullname = secure_filename(file.filename)
        basename = os.path.splitext(fullname)[0].lower()
        ext = os.path.splitext(fullname)[1].lower()

        filename = f"{secure_filename(basename)}_{uuid.uuid4().hex[:12] + ext}"
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)

        print("FILEPATH:", filepath)
        print("EXISTS DIR:", os.path.exists(os.path.dirname(filepath)))

        file.save(filepath)

        

        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print(embeddings)

        loader = PyPDFLoader(filepath)
        documents = loader.load()
        # documents

        vectorstore = Chroma.from_documents(documents, embedding=embeddings)
        # vectorstore

        print(f"VECTOR STORE: {vectorstore.asimilarity_search("ASSURE MODEL")}")

        return {"filepath": filepath}

    