import os
from app.models import Document, DocumentChunk
from app.database.db import db
from app.services.VectorStore.pgvector import PGVectorService
from app.services.Embedding.init_embedding import EmbeddingService
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.document_loaders import PyPDFLoader,TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document as LangchainDocument
from flask import current_app
from markitdown import MarkItDown
from flask import current_app

def process_document_embedding(document_id: str):

    document = Document.query.get(document_id)
    # doc_type = document.doc_type

    if not document:
        print("[WORKER ERROR] Document not found")
        return

    try:
        # 2. Load file
        file_path = document.file_path

        # 3. Load

        # match doc_type:
        #     case "pdf":
        #         loader = PyPDFLoader(file_path)
        #         documents = loader.load()
        #     case "md":
        #         loader = PyPDFLoader(file_path)
        #         documents = loader.load()        


        response = current_app.ai_service.parse_document(file_path)
        
        print(f"DOCUMENT PATH: {file_path}")

        print(f"PARSE DOCS BY CLAUDE: {response}")

        # loader = TextLoader(
        #     file_path,
        #     encoding="utf-8"
        # )

        # documents = loader.load()
        # print(f"DOCUMENT LOAD: {documents}")

        # # 4. chunk

        # headers_to_split_on = [
        #     ("#", "h1"),
        #     ("##", "h2"),
        #     ("###", "h3"),
        # ]

        # med_splitter = MarkdownHeaderTextSplitter(
        #     headers_to_split_on=headers_to_split_on
        # )

        # full_text = "\n".join(doc.page_content for doc in documents)

        # header_docs = med_splitter.split_text(full_text)    

        # print(f"HEADER DOCS: {header_docs}")  

        # recursive_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=800,
        #     chunk_overlap=150,
        #     separators=["\n\n", "\n", ". ", " ", ""],
        #     )
        
        # splits = recursive_splitter.split_documents(header_docs)   
           
        # # print(f"SPLITS: {splits}")  

        # # 5. embed
        # embedding_chunks = PGVectorService().add_vectorstore_document(documents=splits)
        # update = []
        # for chunk in embedding_chunks:
        #     update.append({"id": chunk, "document_id": document_id})

        # print(f"UPDATE FOR EMBEDDING: {update}")
        # db.session.bulk_update_mappings(DocumentChunk, update)
        # db.session.commit()


        # # 3. Mark completed
        # document.status = "completed"
        # document.processed_at = datetime.utcnow()
        # db.session.commit()

        # print(f"[WORKER] Completed {document_id}")
    except Exception as e:
        print("[WORKER ERROR]", e)
        document.status = "failed"
        db.session.commit()


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

