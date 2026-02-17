from langchain_community.llms import Ollama

class OllamaModel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model(*args, **kwargs)
        return cls._instance


    def _init_model(self, model_name="gemma:2b"):
        # load the model once
        self.model = Ollama(model=model_name)
        print("Model loaded")

    def get_model(self):
        return self.model