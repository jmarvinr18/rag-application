import os
from sqlalchemy import create_engine, text
from langchain_postgres import PGVectorStore, PGEngine
from app.services.Embedding.init_embedding import EmbeddingService


class PGVectorService:

    def __init__(self):
        self.connection = os.getenv("PSYCOPG_URL")

        # LangChain engine
        self.pg_engine = PGEngine.from_connection_string(url=self.connection)

        # ✅ Raw SQL engine (NEW)
        self.sql_engine = create_engine(self.connection)

        self.embeddings = EmbeddingService().get_hf_embeddings()

        self.store = self._init_vector_store()

        # create index safely
        self._ensure_hnsw_index()

        # tune search
        self._set_ef_search()

    # -------------------------
    def _init_vector_store(self):
        return PGVectorStore.create_sync(
            engine=self.pg_engine,
            table_name="document_chunks",
            embedding_service=self.embeddings,
            id_column="id",
            content_column="content",
            embedding_column="embedding",
            metadata_json_column="meta",
        )

       

    # -------------------------
    def _ensure_hnsw_index(self):
        sql = """
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 200);
        """

        with self.sql_engine.begin() as conn:
            conn.execute(text(sql))

    # -------------------------
    def _set_ef_search(self):
        with self.sql_engine.begin() as conn:
            conn.execute(text("SET hnsw.ef_search = 40"))

    # -------------------------
    def add_vectorstore_document(self, documents):
        
        store = self.store.add_documents(documents=documents)

        print(f"PG VECTOR STORE: {store}")
        return store

    # -------------------------
    def as_retriever(self):
        return self.store.as_retriever()