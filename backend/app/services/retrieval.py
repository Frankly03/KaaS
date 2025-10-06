from typing import List, Optional, Dict
from langchain_core.documents import Document
from . import vectorstore

def retrieve_relevant_chunks(question: str, k: int, where_filter: Optional[Dict] = None) -> List[Document]:
    """
    High-level function to retrieve relevant document chunks for a given question,
    with an optional filter for metadata.
    """
    search_results = vectorstore.search(question, k, where_filter=where_filter)
    
    if not search_results or not search_results['documents']:
        return []

    documents = search_results['documents'][0]
    metadatas = search_results['metadatas'][0]

    retrieved_docs = []
    for doc_content, metadata in zip(documents, metadatas):
        retrieved_docs.append(
            Document(page_content=doc_content, metadata=metadata)
        )
        
    return retrieved_docs
