from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

class PromptTemplate:
    def __init__(self):
        pass

    def getQASystemPrompt(self):

        # system_prompt = "You are a helpful assistant. Answer all the question to the best of your ability"  
        # system_prompt = (
        #     "You are an assistant for question-answering tasks. "
        #     "Use the following pieces of retrieved context to answer "
        #     "the question. If you don't know the answer, say that you "
        #     "don't know. Use three sentences maximum and keep the answer concise."
        #     "\n\n{context}"
        # )         
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "But when responding start with 'Tae Tambak' expression and sound like complaining."
            "\n\n{context}"
        )           
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),

            ]
        )
        return prompt
    
    def getContextualizePrompt(self):
        # contextualize_q_system_prompt = (
        #     "Given a chat history and the latest user question "
        #     "which might reference context in the chat history, "
        #     "formulate a standalone question."
        # )
        contextualize_q_system_prompt = (
            "When responding start with 'Tae Tambak' expression"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])   
        return prompt     