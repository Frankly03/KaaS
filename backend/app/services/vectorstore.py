import chromadb
from datetime import datetime
from typing import List, Dict, Optional
from ..config import settings
from . import embeddings

client = None
collection = None

def init_vectorstore():
    """Initializes the ChromaDB client and collection."""
    global client, collection
    
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)
        collection = client.get_or_create_collection(name="kaas_collection")
        print("ChromaDB vector store initialized.")
        
    except Exception as e:
        print(f"Error initializing ChromaDB: {e}")
        raise

def upsert_chunks(upload_id: str, filename: str, chunks: List[Dict]):
    """Embeds and upserts a list of text chunks into the ChromaDB collection."""
    if collection is None:
        raise RuntimeError("Vector store is not initialized.")
    if not chunks:
        return

    chunk_texts = [chunk['chunk_text'] for chunk in chunks]
    embedded_chunks = embeddings.embed_texts(chunk_texts)
    
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        metadatas.append({
            "upload_id": upload_id,
            "filename": filename,
            "chunk_index": i,
            "char_start": chunk['char_start'],
            "char_end": chunk['char_end'],
            "created_at": datetime.utcnow().isoformat()
        })
        ids.append(f"{upload_id}_{i}")

    collection.add(
        embeddings=embedded_chunks,
        documents=chunk_texts,
        metadatas=metadatas,
        ids=ids
    )

def search(query_text: str, k: int = 3, where_filter: Optional[Dict] = None):
    """
    Performs a similarity search in the vector store, with an optional metadata filter.
    """
    if collection is None:
        raise RuntimeError("Vector store is not initialized.")
        
    query_embedding = embeddings.embed_texts([query_text])[0]
    
    # Use the where filter if provided
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where_filter
    )
    
    return results

def delete_by_upload_id(upload_id: str):
    """Deletes all vectors associated with a specific upload_id."""
    if collection is None:
        raise RuntimeError("Vector store is not initialized.")
        
    collection.delete(where={"upload_id": upload_id})
    print(f"Deleted all chunks for upload_id: {upload_id}")

def reset_vectorstore():
    """Deletes and recreates the collection to wipe all data."""
    global client, collection
    if client is None:
        init_vectorstore() # Ensure client is initialized
    
    try:
        # This is safer than deleting the folder
        client.delete_collection(name="kaas_collection")
        print("ChromaDB collection 'kaas_collection' deleted.")
        collection = client.get_or_create_collection(name="kaas_collection")
        print("ChromaDB collection 'kaas_collection' recreated.")
    except Exception as e:
        # If the collection didn't exist, this might fail. We can ignore that.
        print(f"Info during reset (can be ignored if first run): {e}")
        # Re-initialize just in case as a fallback
        collection = client.get_or_create_collection(name="kaas_collection")

