from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

class ChatGroqModel:
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model(*args, **kwargs)
        return cls._instance


    def _init_model(self, model_name="llama-3.1-8b-instant"):
        # load the model once
        groq_api_key = os.getenv("GROQ_API_KEY")   
        self.model = ChatGroq(model=model_name, groq_api_key=groq_api_key)
        print("Model loaded")

    def get_model(self):
        return self.model    
    
