from langchain_community.llms import Ollama

class OllamaModel:
    def __init__(self):
        pass



    def init(self, model="gemma:2b"):
        llm = Ollama(model=model)
        return llm