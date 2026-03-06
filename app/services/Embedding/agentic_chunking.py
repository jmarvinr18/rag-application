import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key,temperature=0)

chunks = {}

def create_new_chunk(chunk_id, proposition):
    summary_llm = llm.with_structured_output(ChunkMeta)

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

    chunks[chunk_id] = {
        "summary": chunk_meta.summary,
        "title": chunk_meta.title,
        "propositions": [proposition],
    }

    return chunk_id


class ChunkMeta(BaseModel):
    title: str = Field(description="The title of the chunk.")
    summary: str = Field(description="The summary of the chunk.")

def add_proposition(chunk_id, proposition):
    summary_llm = llm.with_structured_output(ChunkMeta)

    summary_prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "If the current_summary and title is still valid for the propositions return them."
            "If not generate a new summary and a title based on the propositions."
        ),
        (
            "user",
            "current_summary:{current_summary}\n\current_title:{current_title}\n\n propositions:{propositions}",
        )
    ])
    summary_chain = summary_prompt_template | summary_llm

    chunk = chunks[chunk_id]

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


def use_find_chunk_and_push_proposition(proposition):

    class ChunkID(BaseModel):
        chunk_id: int = Field(description="The chunk id.")

    allocation_llm = llm.with_structured_output(ChunkID)
    allocation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You assign propositions to semantic chunks.

                    Return the best matching chunk_id.
                    If none match, return a new chunk_id.
                    Return only the chunk_id.
                    """,
                                ),
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
        chunk_id: chunk["summary"] for chunk_id, chunk in chunks.items()
    }

    best_chunk_id = allocation_chain.invoke(
        {"proposition": proposition, "chunks_summaries": chunks_summaries}
    ).chunk_id

    if best_chunk_id not in chunks:
        best_chunk_id = create_new_chunk(best_chunk_id, proposition)
        return

    chunk = add_proposition(best_chunk_id, proposition)
    return chunk


sentences = [
    "LangChain is a framework for building LLM apps.",
    "It supports retrieval augmented generation.",
    "PGVector stores embeddings inside PostgreSQL."
]

# for i, sentence in enumerate(sentences):
#     find_chunk_and_push_proposition(sentence)

# print(chunks)