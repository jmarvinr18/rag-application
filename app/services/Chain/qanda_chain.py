from langchain_classic.chains.combine_documents import create_stuff_documents_chain


class QAndAChain:
    def __init__(self):
        pass

    def create(self, llm, prompt):
        chain = create_stuff_documents_chain(llm, prompt)
        return chain