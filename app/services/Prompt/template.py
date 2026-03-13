from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

class PromptTemplate:
    def __init__(self):
        pass

    def getQASystemPrompt(self):

        # system_prompt = "You are a helpful assistant. Answer all the question to the best of your ability"  
        system_prompt = (
            "You are a question-answering assistant."
            "Answer ONLY using the provided context."
            "Avoid repeating the previous response content for succeding questions."
            "If the answer cannot be found in the context, respond with:"
            "'I cannot find relevant information in the documents.'"
            "Do NOT use outside knowledge."
            "\n\n{context}"
        )         
        # system_prompt = (
        #     "You are an assistant for question-answering tasks. "
        #     "But when responding start with 'Tae Tambak' expression and sound like complaining."
        #     "\n\n{context}"
        # )           
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),

            ]
        )
        return prompt
    
    def getContextualizePrompt(self):
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question."
            "But do not echo your past responses to the new question."
        )
        # contextualize_q_system_prompt = (
        #     "When responding start with 'Tae Tambak' expression"
        # )
        prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])   
        return prompt     