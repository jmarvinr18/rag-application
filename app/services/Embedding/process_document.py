import os
from app.models import Document, DocumentChunk
from app.database.db import db
from app.services.VectorStore.pgvector import PGVectorService
from app.services.Embedding.init_embedding import EmbeddingService
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader,TextLoader
from .recursive_chunking import use_recursive_chunking

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document as LangchainDocument
from flask import current_app
from markitdown import MarkItDown
from flask import current_app

from langchain_text_splitters import NLTKTextSplitter
from .agentic_chunking import use_find_chunk_and_push_proposition

def process_document_embedding(document_id: str, filename:str):

    document = Document.query.get(document_id)
    # doc_type = document.doc_type

    if not document:
        print("[WORKER ERROR] Document not found")
        return

    try:
        # 2. Load file
        file_path = document.file_path

        # 3. Load
        response = current_app.ai_service.parse_document(file_path)
        print(f"DOCUMENT PATH: {file_path}")
        print(f"PARSE DOCS BY CLAUDE: {response}")        

        # 4. chunk
        splits = split_document(file_path, filename)

        # 5. embed
        store_vector_db(splits, document_id)

        # 3. Mark completed
        update_document_status(document, document_id)

    except Exception as e:
        print("[WORKER ERROR]", e)
        document.status = "failed"
        db.session.commit()


def update_document_status(document, document_id):
    document.status = "completed"
    document.processed_at = datetime.utcnow()
    db.session.commit()

    print(f"[WORKER] Completed {document_id}")  

def store_vector_db(splits, document_id):
    embedding_chunks = PGVectorService().add_vectorstore_document(documents=splits)
    update = []
    for chunk in embedding_chunks:
        update.append({"id": chunk, "document_id": document_id})

    print(f"UPDATE FOR EMBEDDING: {update}")
    db.session.bulk_update_mappings(DocumentChunk, update)
    db.session.commit()

def split_document(file_path, filename):
    loader = TextLoader(
        analyze_and_convert_document(file_path, filename),
        encoding="utf-8"
    )

    documents = loader.load()

    # splits = use_recursive_chunking(documents)

    splitter = NLTKTextSplitter()

    sentences = splitter.split_documents(documents)

    print(f"SENTENCES: {sentences}")

    splits = use_find_chunk_and_push_proposition(sentences)

    print(f"SPLIT WITH PROPOSITION: {splits}")
 
    return splits  

def analyze_and_convert_document(file_path: str, filename: str):

    PATH = "http://localhost:5001/api/v1/documents/uploads"
    UPLOAD_FOLDER = "app/uploads"

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    md_filename = f"{UPLOAD_FOLDER}/{filename}.md"
    response = current_app.ai_service.parse_document(file_path)

    for r in response:
        try:
            # Open the file in append mode ('a')
            with open(md_filename, "a", encoding="utf-8") as file:
                # Append content to the file
                file.write(r + "\n")
            print(f"Appended to {md_filename} successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")

    return md_filename



def convert_to_md(document: str, filename:str):

    PATH = "http://localhost:5001/api/v1/documents/uploads"

    UPLOAD_FOLDER = "app/uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    md = MarkItDown()
    result = md.convert(document)
    md_filename = f"{UPLOAD_FOLDER}/{filename}.md"
    print(result)

    try:
        # Open the file in write mode ('w')
        with open(md_filename, "w", encoding="utf-8") as file:
            # Write content to the file
            file.write(result.text_content)
        print(f"File {md_filename} created and written to successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    return f"{PATH}/{filename}.md"

