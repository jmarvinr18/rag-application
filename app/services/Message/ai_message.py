from app.services.LLM import OllamaModel
from app.services.Prompt import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
        # llm = LLMModel().get()
        # prompt = Prompt().get()
        # output_parser = StrOutputParser()   
class AIMessage:
    def __init__(self):
        pass



    def get(self, human_message):
        llm = OllamaModel().init()
        prompt = PromptTemplate().get()
        output_parser = StrOutputParser()   

        chain = prompt|llm|output_parser

        return chain.invoke({"messages": [HumanMessage(content=human_message)]})