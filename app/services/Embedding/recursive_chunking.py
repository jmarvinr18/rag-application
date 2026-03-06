
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

def use_recursive_chunking(documents):
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    med_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    full_text = "\n".join(doc.page_content for doc in documents)
    header_docs = med_splitter.split_text(full_text)        
    print(f"HEADER DOCS: {header_docs}")
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    splits = recursive_splitter.split_documents(header_docs)
    print(f"SPLITS: {splits}") 

    return splits
