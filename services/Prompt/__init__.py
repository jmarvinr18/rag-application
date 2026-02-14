from langchain_core.prompts import ChatPromptTemplate


class Prompt:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant. Please respond to the question asked."),
                ("user", "Question:{question}")
            ]
        )

    def get(self):

        return self.prompt