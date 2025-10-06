from typing import List
from langchain_core.documents import Document
from ..config import settings

# --- Prompt Template ---

PROMPT_TEMPLATE = """
You are a helpful, concise assistant. Answer using only the provided context. If the context does not contain enough information, say "I don't know" or "The provided context does not contain sufficient information." instead of making things up. Cite the sources inline using the format [filename:chunk_index]. Keep answers under 150 words unless asked for more detail.


Context:
{context}

Question: {question}

Answer and cite sources:
"""

def _format_context(retrieved_docs: List[Document]) -> str:
    """Formats the retrieved documents into a string for the prompt context."""
    context_parts = []
    for i, doc in enumerate(retrieved_docs):
        filename = doc.metadata.get("filename", "N/A")
        chunk_index = doc.metadata.get("chunk_index", "N/A")
        context_parts.append(f"[{i+1}] source: {filename}, chunk: {chunk_index}\n{doc.page_content}")
    return "\n\n".join(context_parts)

def _format_prompt(question: str, context: str) -> str:
    """Fills the prompt template with the question and formatted context."""
    return PROMPT_TEMPLATE.format(context=context, question=question)

def generate_answer(question: str, retrieved_docs: List[Document]) -> str:
    """
    Generates an answer using either the Groq API or a local Hugging face model.
    """
    context = _format_context(retrieved_docs)
    prompt = _format_prompt(question, context)

    # # --- DEBUG: Check context before sending to model ---
    # print("--- DEBUG: Question ---")
    # print(question)
    # print("--- DEBUG: Context (first 1000 chars) ---")
    # print(context[:1000]) 

    # Use Groq if API key is provided
    if settings.GROQ_API_KEY:
        try:
            return _generate_with_groq(prompt)
        except Exception as e:
            print(f"Groq API call failed: {e}. Falling back to HF if enabled.")
            if not settings.HF_FALLBACK:
                return "ERROR: Could not generate answer."
    
    # Fallback to Hugging Face model
    if settings.HF_FALLBACK:
        return _generate_with_hf(prompt)
    
    return "Error: No generation model is configured."


# --- Groq Generation ---
def _generate_with_groq(prompt: str) -> str:
    """Calls the Groq API to generate a response."""
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on provided context. Cite sources like [filename:chunk_index]."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=250,
    )
    return chat_completion.choices[0].message.content

# ---Hugging Face Fallback ---
# This part is loaded lazily to avoid importing torch unless needed
hf_pipeline = None

def _initialize_hf_pipeline():
    """Initializes the Hugging Face pipeline on first use."""
    global hf_pipeline
    if hf_pipeline is None:
        try:
            from transformers import pipeline
            print("Initializing Hugging Face pipeline for the first time... (This may take a moment)")
            # Use a smaller, CPU-friendly model for the fallback
            hf_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")
            print("Hugging Face pipeline initialized.")
        except ImportError:
            raise ImportError("Please install 'transformers' and 'torch' to use the Hugging Face fallback.")
        except Exception as e:
            print(f"Error initializing HF pipeline: {e}")
            hf_pipeline = "failed"


def _generate_with_hf(prompt: str) -> str:
    """Generates a response using a local Hugging Face model."""
    if hf_pipeline is None:
        _initialize_hf_pipeline()

    if hf_pipeline == "failed" or hf_pipeline is None:
        return "Error: hugging Face fallback model could not be loaded."
    

    # simplified prompt specifically for Flan-T5
    # We find the context and question from the original prompt to recontruct it.

    try:
        # This is a bit of a hack to extract the original parts for the new prompt format
        context_part = prompt.split("Context:")[1].split("Question:")[0].strip()
        question_part = prompt.split("Question:")[1].split("Answer and cite sources:")[0].strip()

        # New, simpler prompt format
        simple_prompt = f"Please answer the following question based only on the provided context. \n\nContext: {context_part}\n\nQuestion: {question_part}\n\nAnswer:"

    except IndexError:
        # If the prompt isn't in the expected format, fall back to the original
        simple_prompt = prompt
    
    # flan-t5 models have a max sequence length, so we need to truncate the prompt 
    max_length = 512
    if len(simple_prompt) > max_length * 3:
        simple_prompt = simple_prompt[:max_length * 3]

    try:
        result = hf_pipeline(simple_prompt, max_length=150, num_return_sequences=1)
        return result[0]['generated_text']
    except Exception as e:
        print(f"Error during HF generation: {e}")
        return "Error generating answer with the local model."
    

