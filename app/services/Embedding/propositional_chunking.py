from langsmith import Client
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=openai_api_key,temperature=0)

client = Client()

prompt = client.pull_prompt("wfh/proposal-indexing")


# You can explore the prompt template behind this by running the following:
# obj.get_prompts()[0].messages[0].prompt.template

llm = ChatOpenAI(model="gpt-4o")


# A Pydantic model to extract sentences from the passage
class Sentences(BaseModel):
    sentences: list[str]

extraction_llm = llm.with_structured_output(Sentences)


# Create the sentence extraction chain
extraction_chain = prompt | extraction_llm


# Test it out
sentences = extraction_chain.invoke(
    """
    On July 20, 1969, astronaut Neil Armstrong walked on the moon . 
    He was leading the NASA's Apollo 11 mission. 
    Armstrong famously said, "That's one small step for man, one giant leap for mankind" as he stepped onto the lunar surface.
    """
)

print(sentences)