from app.models import Document, DocumentChunk
from app.database.db import db
from app.services.VectorStore.pgvector import PGVectorService
from app.services.Embedding.init_embedding import EmbeddingService
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document as LangchainDocument
from flask import current_app

def process_document_embedding(document_id: str):

    document = Document.query.get(document_id)

    if not document:
        print("[WORKER ERROR] Document not found")
        return

    try:
        # 2. Load file
        file_path = document.file_path

        # TODO: Langchain pipeline here

        # 3. Load
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        print(f"DOCUMENT LOAD: {documents}")

        # 4. chunk
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        splits = text_splitter.split_documents(documents)      
        
        print(f"SPLITS: {splits}")  

        # 5. embed
        embedding_chunks = PGVectorService().add_vectorstore_document(documents=splits)
        update = []
        for chunk in embedding_chunks:
            update.append({"id": chunk, "document_id": document_id})

        print(f"UPDATE FOR EMBEDDING: {update}")
        db.session.bulk_update_mappings(DocumentChunk, update)
        db.session.commit()


        # 3. Mark completed
        document.status = "completed"
        document.processed_at = datetime.utcnow()
        db.session.commit()

        print(f"[WORKER] Completed {document_id}")
    except Exception as e:
        print("[WORKER ERROR]", e)
        document.status = "failed"
        db.session.commit()