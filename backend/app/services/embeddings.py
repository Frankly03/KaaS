from sentence_transformers import SentenceTransformer
from typing import List
from ..config import settings

# Load the model only once when the module is imported
# This is a relatively small model, so it's fine to load at startup.

try:
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print("Embedding model loaded successfully")
except Exception as e:
    model = None
    print(f"Failed to load SentenceTransformer model: {e}")

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Computers embeddings for a list of texts using the pre-loaded SentenceTransformer model.
    """
    if model is None:
        raise RuntimeError("Embedding model is not available.")
    
    # The encode method handles batches internally
    embeddings = model.encode(texts, convert_to_tensor=False)
    # convert_to_tensor=False returns numpy arrays, which we convert to lists
    return [embedding.tolist() for embedding in embeddings]