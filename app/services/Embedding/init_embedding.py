from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:

    def __init__(self):
        pass

    def get_hf_embeddings(self, model_name="all-MiniLM-L6-v2"):
        return HuggingFaceEmbeddings(model_name=model_name)
    