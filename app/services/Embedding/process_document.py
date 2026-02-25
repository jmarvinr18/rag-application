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

        # 5. embed
        embeddings = EmbeddingService.get_hf_embeddings()

        print("embeddings")

        # 6. store in PGVector
        for idx, page in enumerate(documents):
            print(f"PAGE>>>> {page}")
            print(f"PAGE CONTENT>>>> {page.page_content}")
            # vector = embeddings.embed_query(page.page_content)
            lcdocs = [LangchainDocument(page_content=page.page_content, metadata={"id": document.id})]
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=idx,
                content=page.page_content,
                embedding="vector",
                token_count=len(page.page_content.split()),
                meta={"source": document.file_path}
            )
            db.session.add(chunk)

            print(f"LC DOCS>>>>>{lcdocs}")  

            PGVectorService().add_vectorstore_document(document=documents)


        # 3. Mark completed
        document.status = "completed"
        document.processed_at = datetime.utcnow()
        db.session.commit()

        print(f"[WORKER] Completed {document_id}")
    except Exception as e:
        print("[WORKER ERROR]", e)
        document.status = "failed"
        db.session.commit()