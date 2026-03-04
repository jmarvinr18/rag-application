from langchain.chat_models import init_chat_model
from langchain_aws import ChatBedrock
import os
from dotenv import load_dotenv

load_dotenv()

class AWSBedrockModel:
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model(*args, **kwargs)
        return cls._instance


    def _init_model(self, model_name):
        # load the model once
        self.model = ChatBedrock(
            model_id=model_name,
            region_name="ap-southeast-1",
            provider="anthropic",

        )

    def get_model(self):
        return self.model    
    
