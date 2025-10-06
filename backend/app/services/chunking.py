from typing import List, Dict

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[Dict]:
    """
    Splits a long text into smaller chunks with a specified overlap.
    Returns a list of dictionaries, each containing the chunk_text and its character offsets.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The maximum size of each chunk in characters.
        chunk_overlap (int): The number of characters to overlap between consecutive chunks

    Returns:
        List[Dict]: A list of chunks, where each chunk is a dictionary with
        'chunk_text', 'char_start', and 'char_end'.
    """
    if not text:
        return []
    
    chunks = []
    start_index = 0

    while start_index < len(text):
        end_index = start_index + chunk_size
        chunk_text = text[start_index:end_index]

        chunks.append({
            "chunk_text": chunk_text,
            "char_start": start_index,
            "char_end": start_index + len(chunk_text)
        })

        # Move start_index for the next chunk
        start_index += chunk_size - chunk_overlap

        # Ensure we don't create a tiny, redundant chunk at the end
        if start_index + chunk_overlap >= len(text):
            break
    return chunks