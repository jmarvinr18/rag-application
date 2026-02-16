from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

class PromptTemplate:
    def __init__(self):
        pass

    def get(self):

        system_prompt = "You are a helpful assistant. Answer all the question to the best of your ability"      
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("messages")
            ]
        )
        return prompt