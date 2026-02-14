from langchain_community.llms import Ollama

class LLMModel:
    def __init__(self):
        print("Loading model...")
        self.llm = Ollama(model="gemma:2b")


    def get(self):
        return self.llm