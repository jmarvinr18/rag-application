import os
from langchain_postgres import PGVector, PGVectorStore, PGEngine
from app.services.Embedding.init_embedding import EmbeddingService
from langchain_postgres.v2.engine import Column


class PGVectorService:

    def __init__(self):
        pass


    def get_vectorstore(self):
        connection = os.getenv("PSYCOPG_URL")
        pg_engine = PGEngine.from_connection_string(url=os.getenv("PSYCOPG_URL"))
        return PGVectorStore(engine=pg_engine)


    def add_vectorstore_document(self,document):
        print("will add embeddings")

        result = self.get_vectorstore().add_documents(documents=document)
        
        if isinstance(result[0], tuple):
            # Old version - extract from tuple
            document_ids = [str(item[0]) if item else str(i) for i, item in enumerate(result)]
        else:
            # New version - direct IDs
            document_ids = result

        print(document_ids)

    def _init_vector_store(self):

        pg_engine = PGEngine.from_connection_string(url=os.getenv("PSYCOPG_URL"))
        embeddings = EmbeddingService().get_hf_embeddings()


        store = PGVectorStore.create_sync(
            engine=pg_engine,
            table_name="document_chunks",
            embedding_service=embeddings,
            id_column="id",
            content_column="content",
            embedding_column="embedding",
            metadata_json_column="meta"
        )

        return store