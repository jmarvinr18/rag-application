import os
import io
import base64
import mimetypes
from app.services.Prompt import PromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from flask import current_app
from app.models import Message
from app.database import db
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_history_aware_retriever
from langchain_huggingface import HuggingFaceEmbeddings
from app.services.VectorStore.pgvector import PGVectorService
from app.services.Embedding.init_embedding import EmbeddingService
from pdf2image import convert_from_path
from dotenv import load_dotenv
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

load_dotenv()

class AIMessageService:

    def __init__(self, model):
        self.model = model
        self.embeddings = EmbeddingService().get_hf_embeddings()

        # PGVectorService()._init_vector_store().as_retriever()

        self.vector_store = PGVectorService()._init_vector_store()
        
        vector_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20}
        )

        docs = self.vector_store.similarity_search("", k=1000)

        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 5        

        self.retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.7, 0.3]
        )

        # self.retriever = self.vector_store.as_retriever(
        #     search_type="mmr",
        #     search_kwargs={"k": 5,"fetch_k": 20, "lambda_mult": 0.7},            
        # )
        self.rag_chain = self._build_chain()
        self.with_history = self._init_runnable_message_history()


    def _build_chain(self):
        qa_system_prompt = PromptTemplate().getQASystemPrompt()
        contextualize_prompt = PromptTemplate().getContextualizePrompt()
        history_aware_retriever = create_history_aware_retriever(self.model, 
                                                                 self.retriever, 
                                                                 contextualize_prompt)
        question_answer_chain = create_stuff_documents_chain(self.model, qa_system_prompt)
        return create_retrieval_chain(history_aware_retriever, question_answer_chain)


    def getSessionHistory(self, conversation_id: str="") -> BaseChatMessageHistory:

        history = InMemoryChatMessageHistory()
        messsages = (Message.query.filter_by(conversation_id=conversation_id)
                                  .order_by(Message.created_at)
                                  .all())
        for m in messsages:
            if m.role == "user":
                history.add_message(message=HumanMessage(content=m.content))

        return history
    
    def _init_runnable_message_history(self):
        return RunnableWithMessageHistory(self.rag_chain,
                                    self.getSessionHistory,
                                    input_messages_key="input",
                                    history_messages_key="chat_history",
                                    output_messages_key="answer",  
                                    )        

    def ask(self, conversation_id, human_message):

        config = {"configurable": {"session_id": conversation_id}}

        # Step 1: retrieve relevant docs
        docs = self.retrieve_relevant_docs(human_message)

        # Step 2: guardrail
        if not docs:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "sources": []
            }
        
        # Step 3: normal RAG execution
        response = self.with_history.invoke(
            {"input": human_message},
            config=config
        )

        return {
            "answer": response["answer"],
            "sources": [doc.metadata for doc in docs]
        }

        # return self.with_history.invoke(
        #     {"input": human_message},
        #     config=config
        # )
    
    def retrieve_relevant_docs(self,question):

        docs = self.retriever.invoke(question)

        if not docs:
            return []

        return docs        

        # SIMILARITY_THRESHOLD = 0.50
        
        # docs_and_scores = self.vector_store.similarity_search_with_score(question, k=5)

        # print(f"DOCS AND SCORE: {docs_and_scores}")

        # filtered_docs = [
        #     doc for doc, score in docs_and_scores
        #     if score < SIMILARITY_THRESHOLD
        # ]

        # return filtered_docs

    def parse_document(self, image_path):

        print(f"IMAGE PATH: {image_path}")


        if not image_path:
            return None
        
        if not os.path.exists(image_path):
            raise ValueError(f"Image not found: {image_path}")
        
        mime_type, _ = mimetypes.guess_type(image_path)
        results = []

        if mime_type in ["image/png", "image/jpeg", "image/webp"]:
            image_b64 = self._encode_image(image_path)
            response = self._invoke_bedrock_image(image_b64, mime_type)
            results.append(response.content)

        elif mime_type == "application/pdf":
            pages = convert_from_path(
                image_path,
                dpi=200,
                fmt="png",
                poppler_path=r"C:\poppler-25.12.0\Library\bin"
            )

            for i, page in enumerate(pages):
                buffer = io.BytesIO()
                page.save(buffer, format="PNG")


                image_b64 = base64.b64encode(buffer.getvalue()).decode()

                response = self._invoke_bedrock_image(image_b64,"image/png")

                print(f"RESPONSE: {response.content}")

                results.append(response.content)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")
        
        return results
        
    

    def _invoke_bedrock_image(self, image_b64, mime_type):
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "You are an expert AI assistant, you are tasked with extracting the entire text from any PDF document. The document can be simple, complex, or even scanned, this shouldn't matter to you."
                        "You will be given the entire PDF as input. Start examining the document page by page, when you come across text, extract it as is don't convert it into another format like HTML or Markdown. If you come across images, replace them with a very detailed description of the image while taking into consideration the context around it."
                        "When you come across tables, describe them too like the image. The description should be very detailed and in a way that someone will understand the table without seeing it."
                        "Make sure to keep the structure of the document, if there are sections, subsections, bullet points, or numbered lists, make sure to keep them as is. If there are any headers, footers, page numbers, remove them."
                        "If there are line breaks mid-sentence, please remove it and display the entire sentence or paragraph in smooth flow."
                        "If there's table that is cut to the next page and has no header, please use the header of the table from the previous page."
                        "The final output should be a clean, well-structured text that represents the content of the entire PDF document as closely as possible to how a human would see it with their eyes when reading the document. Don't say anything else, just output the text you extracted from the PDF."
                        "Here is the PDF:"
                    ),
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": image_b64,
                    },
                },
            ]
        )

        return self.model.invoke([message]) 
    
    def _encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()