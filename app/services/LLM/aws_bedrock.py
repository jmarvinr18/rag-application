from langchain.chat_models import init_chat_model
from langchain_aws import ChatBedrock
import os
from dotenv import load_dotenv

class AWSBedrockModel:
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model(*args, **kwargs)
        return cls._instance


    def _init_model(self, model_name):

        load_dotenv(".env",override=True)

        os.environ["BEDROCK_API_KEY"] = os.getenv("BEDROCK_API_KEY")
        os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        os.environ["AWS_DEFAULT_REGION"] = os.getenv("AWS_DEFAULT_REGION")
        
        self.model = ChatBedrock(
            model_id=model_name,
            region_name="ap-southeast-1",
            provider="anthropic",

        )

    def get_model(self):
        return self.model    
    
