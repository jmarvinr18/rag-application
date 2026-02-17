from app.services.Prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from flask import current_app
from app.models import Message
from app.database import db

class AIMessageService:
    def __init__(self):

        self.store = {}


    def getSessionHistory(self, conversation_id: str="") -> BaseChatMessageHistory:

        history = InMemoryChatMessageHistory()
        messsages = (Message.query.filter_by(conversation_id=conversation_id)
                                  .order_by(Message.created_at)
                                  .all())
        for m in messsages:
            if m.role == "user":
                history.add_message(message=HumanMessage(content=m.content))

        return history



    def invokeWithHistory(self, conversation_id, human_message):

        model  = current_app.ai_service.get_model() 

        prompt = PromptTemplate().get()
        output_parser = StrOutputParser()
        config = {"configurable": {"session_id": conversation_id}}

        chain = prompt|model|output_parser


        with_message_history = RunnableWithMessageHistory(
            chain,
            self.getSessionHistory,
            input_messages_key="input",
            history_messages_key="chat_history"

        )

        response = with_message_history.invoke({"input": human_message, "language": "tagalog"}, 
                                           config=config)
        
        return response

