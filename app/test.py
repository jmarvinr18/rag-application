from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_text_splitters import NLTKTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize
from services.Embedding.agentic_chunking import use_find_chunk_and_push_proposition
loader = TextLoader(
    "C:/Users/USER/Documents/machine-learning/projects/slgs/rag-poc/app/uploads/from_continuous_deployment_with_jenkins_pipelines_to_mcp_and_llm.md",
    encoding="utf-8"
)
import json

documents = loader.load()


text = """
rom Continuous Deployment
with Jenkins Pipelines to MCP
and LLM.

marjune
Follow

5 min read
·
Jun 26, 2025

With my progress in creating my own MCP (Model Context

Protocol) server to manage a Kubernetes cluster, my primary goal is to

learn how to utilize LLM for tasks beyond code generation and public

knowledge questions. As I discussed in my previous article,

How I Built a Personal Docker-based MCP to manage a K8s cluster.

I created a few simple tools to interface with a Kubernetes cluster.

Moving forward, I want to add more capability where, instead of using

a CI/CD pipeline to deploy my application, LLM will take care of the

deployment on my behalf, based on certain standards, so that LLM will

not assume how to proceed. Since LLM can perfectly reason out, I’ll

communicate in a way that makes it seem like my intelligent assistant

is handling the task, removing the technical overhead associated with

operating tools like Jenkins or any other CI/CD.

Application Deployment

I created a pipeline before where I used Jenkins as my CI/CD tool for

deployment,

Blue/Green Deployment in Kubernetes using Jenkins Declarative

Pipeline.

With the same application as Blue/Green. I’ll add more tools to

my MCP, like deployment from start to finish.

MCP Tools

https://github.com/mrjbtc/mcp-k8s/tree/main

To help the LLM understand how to deploy my application, I created a

tool that outputs a clear, step-by-step description of the deployment

process.
"""


sentences = sent_tokenize(text)

print(sentences)
for s in sentences:
    json_data = json.dumps(s, indent=2)


print(use_find_chunk_and_push_proposition(s))

# print(documents)


# splitter = NLTKTextSplitter()

# # print(f"DOCUMENTS: {documents}")

# # sentences = splitter.split_documents(documents)

# recursive_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=800,
#     chunk_overlap=150,
#     separators=["\n\n", "\n", ". ", " ", ""],
#     )

# splits = recursive_splitter.split_documents(documents)


# print(f"SPLITS: {splits}")

# for s in splits:
#     print(f"SPLIT: {s.page_content}")


# print(documents)

