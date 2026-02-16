from langchain_classic.chains import create_retrieval_chain



class RetrievalChain:
    def __init__(self):
        pass

    def create(self, llm, prompt):
        chain = create_retrieval_chain(llm, prompt)
        return chain
    
    def invoke(self, input):
        return self.create().invoke({"input": input})