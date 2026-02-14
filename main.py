
import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st


load_dotenv()

## Langsmith tracking
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACKING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")



def prompt_template():
## Prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Please respond to the question asked."),
            ("user", "Question:{question}")
        ]
    )

    return prompt

## Ollama Llama2 model

llm = Ollama(model="gemma:2b")
output_parser = StrOutputParser()

chain = prompt_template()|llm|output_parser
    

## Streamlit framework
st.title("SLGS DevOps AI Initiative: Langchain POC with Gemma LLM Model")
input_text = st.text_input("What question you have in mind?")



if input_text:
    st.write(chain.invoke({"question": input_text}))

# def main():
    
#     if input_text:
#         st.write(chain.invoke({"question": input_text}))

# if __name__ == "__main__":
#     main()
