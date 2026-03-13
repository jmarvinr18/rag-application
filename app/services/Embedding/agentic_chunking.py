import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class ChunkMeta(BaseModel):
    title: str = Field(description="The title of the chunk.")
    summary: str = Field(description="The summary of the chunk.")


class AgenticChunker:

    def __init__(self):
        self.chunks = []
        self.llm = self.__init_llm()

    def __init_llm(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key,temperature=0)


    def create_new_chunk(self, chunk_id, proposition):
        summary_llm = self.llm.with_structured_output(ChunkMeta)
        summary_prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "Generate a new summary and a title based on the propositions",
            ),
            (
                "user",
                "propositions:{propositions}"
            )
        ])

        summary_chain = summary_prompt_template | summary_llm
        chunk_meta = summary_chain.invoke(
            {
                "propositions": [proposition]
            }
        )

        chunk = {
            "id": chunk_id,
            "summary": chunk_meta.summary,
            "title": chunk_meta.title,
            "propositions": [proposition],
        }

        self.chunks.append(chunk)

        return chunk




    def add_proposition(self, chunk_id, proposition):

        summary_llm = self.llm.with_structured_output(ChunkMeta)
        summary_prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "If the current_summary and title is still valid for the propositions return them."
                "If not generate a new summary and a title based on the propositions."
            ),
            (
                "user",
                "current_summary:{current_summary}\n current_title:{current_title}\n propositions:{propositions}",
            )
        ])
        summary_chain = summary_prompt_template | summary_llm

        chunk = self.get_chunk_by_id(chunk_id)

        current_summary = chunk["summary"]
        current_title = chunk["title"]
        current_propositions = chunk["propositions"]
        all_propositions = current_propositions + [proposition]

        chunk_meta = summary_chain.invoke(
            {
                "current_summary": current_summary,
                "current_title": current_title,
                "propositions": all_propositions
            }
        )

        chunk["summary"] = chunk_meta.summary
        chunk["title"] = chunk_meta.title
        chunk["propositions"] = all_propositions

        return chunk


    def use_find_chunk_and_push_proposition(self, proposition):

        class ChunkID(BaseModel):
            chunk_id: int = Field(description="The chunk id.")

        allocation_llm = self.llm.with_structured_output(ChunkID)
        allocation_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You assign propositions to semantic self.chunks.

                        Return the best matching chunk_id.
                        If none match, return a new chunk_id.
                        Return only the chunk_id.
                        """,),
                                    (
                        "user",
                        """Proposition:
                        {proposition}

                        Existing chunks:
                        {chunks_summaries}
                    """,
                ),
            ]
        )

        allocation_chain = allocation_prompt | allocation_llm

        chunks_summaries = {
            chunk["id"]: chunk["summary"] for chunk in self.chunks
        }

        best_chunk_id = allocation_chain.invoke(
            {"proposition": proposition, "chunks_summaries": chunks_summaries}
        ).chunk_id

        # if best_chunk_id not in self.chunks:
        #     best_chunk_id = self.create_new_chunk(best_chunk_id, proposition)
        #     return

        chunk = self.get_chunk_by_id(best_chunk_id)        

        if chunk is None:
            return self.create_new_chunk(best_chunk_id, proposition)
        
        return self.add_proposition(best_chunk_id, proposition)

    
    def get_chunk_by_id(self, chunk_id):
        for chunk in self.chunks:
            if chunk["id"] == chunk_id:
                return chunk
        return None    
    
    def get_chunks(self):
        return self.chunks
