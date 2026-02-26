import uuid
import os
from flask import request,jsonify
from flask.views import MethodView
from flask_smorest import Blueprint,abort

from app.database.db import db
from app.schema.document import DocumentSchema
from app.models import Document as DocumentModel
from app.routes import api
from app.task_queue import task_queue
from app.services.Embedding.process_document import process_document_embedding

from werkzeug.utils import secure_filename

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
        return DocumentModel.query.all()

    

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
        
        

        full_filename = f"{secure_filename(basename)}_{uuid.uuid4().hex[:12] + ext}"
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filepath = os.path.join(upload_dir, full_filename)

        print("FILEPATH:", filepath)
        print("EXISTS DIR:", os.path.exists(os.path.dirname(filepath)))

        file.save(filepath)

        filename= os.path.basename(filepath)


        # save DB record
        document = DocumentModel(title=filename, 
                                 source=filepath, 
                                 file_path=filepath, 
                                 status="pending")
        db.session.add(document)
        db.session.commit()
        

        # ✅ enqueue background job
        job = task_queue.enqueue(
            process_document_embedding,
            str(document.id),
            job_timeout=600  # adjust if large docs
        )
        
        return jsonify({
            "message": "Upload successful",
            "document_id": str(document.id),
            "job_id": job.id,
            "status": "pending"
        })

    