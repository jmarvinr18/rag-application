import uuid
import os
from flask import request,jsonify,send_from_directory
from flask.views import MethodView
from flask_smorest import Blueprint,abort

from app.database.db import db
from app.schema.document import DocumentSchema
from app.models import Document as DocumentModel
from app.routes import api
from app.task_queue import task_queue
from app.services.Embedding.process_document import process_document_embedding, convert_to_md

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


    def delete(self,document_id):
        doc = DocumentModel.query.get(document_id)

        if doc:
            db.session.delete(doc)
            db.session.commit()
            return {"message": f"Deleted document {doc.title}", "status": 200}
        else:
            return {"message": f"Document not found", "status": 404}

        

@blp.route("")
class DocumentList(MethodView):

    @blp.response(200, DocumentSchema(many=True))
    def get(self):
        return DocumentModel.query.all()

    

    # @blp.arguments(DocumentSchema)
    # @blp.response(201, DocumentSchema)

    def post(self):
        UPLOAD_FOLDER = "app/uploads"

        if "source" not in request.files:
            return {"error":  "No file part"}, 400

        title = request.form.get("title")
        file = request.files["source"]

        fullname = secure_filename(file.filename)
        basename = os.path.splitext(fullname)[0].lower()
        ext = os.path.splitext(fullname)[1][1:].lower()

        path = "http://localhost:5001/api/v1/documents/uploads"
        
        
        rand = uuid.uuid4().hex[:12]

        full_filename = f"{secure_filename(basename)}_{rand}.{ext}"

        upload_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filename=os.path.basename(basename)
        
        filename_without_ext = os.path.splitext(os.path.basename(filename))[0]

        modified_filename=f"{filename_without_ext}_{rand}.{ext}"

        filepath = os.path.join(upload_dir, full_filename)

        public_filepath = f"{path}/{modified_filename}"


        

        print("FILEPATH:", filepath)
        print("PUBLIC FILEPATH:", public_filepath)
        print("EXISTS DIR:", os.path.exists(os.path.dirname(filepath)))

        file.save(filepath)

        md_source = convert_to_md(filepath, filename)
        # save DB record
        document = DocumentModel(title=filename, 
                                 source=md_source, 
                                 file_path=filepath, 
                                 doc_type=ext,
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



UPLOAD_FOLDER = os.path.abspath("C:/Users/USER/Documents/machine-learning/projects/slgs/rag-poc/app/uploads")
@blp.route("/uploads/<path:filename>")
def serve_upload(filename):
    # return "FILE PDF"

    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        mimetype="application/pdf"
    )