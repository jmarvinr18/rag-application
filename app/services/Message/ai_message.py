import os
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
from dotenv import load_dotenv

load_dotenv()

class AIMessageService:

    def __init__(self, model):
        self.model = model
        self.embeddings = EmbeddingService().get_hf_embeddings()

        # PGVectorService()._init_vector_store().as_retriever()

        self.vector_store = PGVectorService()._init_vector_store()
        
        self.retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4,"fetch_k": 12},            
        )
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

        return self.with_history.invoke(
            {"input": human_message},
            config=config
        )
    