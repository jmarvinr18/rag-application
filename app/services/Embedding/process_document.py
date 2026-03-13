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
from .agentic_chunking import AgenticChunker
import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize

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
        chunks = split_document(file_path, filename)

        # 5. embed
        store_vector_db(chunks, document_id)

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

def store_vector_db(chunks, document_id):
    
    embedding_model = EmbeddingService().get_hf_embeddings()
    # embedding_chunks = PGVectorService().add_vectorstore_document(documents=splits)
    # update = []
    # for chunk in embedding_chunks:
    #     update.append({"id": chunk, "document_id": document_id})

    # print(f"UPDATE FOR EMBEDDING: {update}")
    # db.session.bulk_update_mappings(DocumentChunk, update)
    # db.session.commit()

    for chunk in chunks:
        content = f"""
            Title: {chunk['title']}
            Summary: {chunk['summary']}
            Propositions: {" ".join(chunk["propositions"])}
        """

        vector = embedding_model.embed_query(content)

        db_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk['id'],
            content=content,
            embedding=vector,
            meta=chunk
        )

        db.session.add(db_chunk)
        db.session.commit()    

def split_document(file_path, filename):
    chunks = []
    loader = TextLoader(
        analyze_and_convert_document(file_path, filename),
        encoding="utf-8"
    )

    documents = loader.load()

    chunker = AgenticChunker()

    for doc in documents:
        print(f"DOCS:.....{doc}")
        sentences = sent_tokenize(doc.page_content)
        for s in sentences:

            chunk = chunker.use_find_chunk_and_push_proposition(s)
            print(f"CHUNK====|>>{chunk}")

            index = next((i for i, c in enumerate(chunks) if c["id"] == chunk["id"]), None)

            if index is not None:
                chunks[index] = chunk
            else:
                chunks.append(chunk)

    print(f"CHUNKS: {chunks}")
 
    return chunks  

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
                file.write(r)
            print(f"Appended to {md_filename} successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")

    return md_filename



def convert_to_md(document: str, filename:str):

    PATH = "http://localhost:5001/api/v1/documents/uploads"

    # UPLOAD_FOLDER = "app/uploads"
    # os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # md = MarkItDown()
    # result = md.convert(document)
    # md_filename = f"{UPLOAD_FOLDER}/{filename}.md"
    # print(result)

    # try:
    #     # Open the file in write mode ('w')
    #     with open(md_filename, "w", encoding="utf-8") as file:
    #         # Write content to the file
    #         file.write(result.text_content)
    #     print(f"File {md_filename} created and written to successfully.")

    # except Exception as e:
    #     print(f"An error occurred: {e}")

    return f"{PATH}/{filename}.md"

