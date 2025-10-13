import streamlit as st
import os
import uuid
import time
from backend.app.services import (
    pdf_loader,
    text_loader,
    chunking,
    vectorstore,
    retrieval,
    generation
)
from backend.app import db
from backend.app.config import settings
from sqlalchemy.orm import Session

# --- Page Configuration ---
st.set_page_config(
    page_title="KaaS - Knowledge as a Service",
    page_icon="🧠",
    layout="wide",
)

# --- Database Session ---
# Create a session for the Streamlit app to use
@st.cache_resource
def get_db_session():
    return next(db.get_db())

DB_SESSION = get_db_session()

# Initilalize vector store at the start
vectorstore.init_vectorstore()

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# --- Helper Functions ---
def get_all_uploads():
    """Fetches the list of all uploaded documents from the database."""
    return DB_SESSION.query(db.Upload).all()

def refresh_uploads():
    """Refreshes the list of uploaded files in the session state."""
    st.session_state.uploaded_files = get_all_uploads()

def delete_document(upload_id: str, filename: str):
    """Deletes a document from the vector store and the database."""
    try:
        # 1. Delete from vector store
        vectorstore.delete_by_upload_id(upload_id)

        # 2. Delete from SQL database
        upload_to_delete = DB_SESSION.query(db.Upload).filter(db.Upload.id == upload_id).first()
        if upload_to_delete:
            DB_SESSION.delete(upload_to_delete)
            DB_SESSION.commit()

        st.toast(f"Successfully deleted '{filename}'")
        refresh_uploads()
    except Exception as e:
        st.error(f"Failed to delete '{filename}': {e}")

with st.sidebar:
    st.title("📄 Document Management")
    st.markdown("Upload new documents and manage existing ones.")

    # File Uploader 
    uploaded_file = st.file_uploader(
        "Upload a PDF or TXT document", type=['pdf', 'txt'], accept_multiple_files=False
    )
    if uploaded_file is not None:
        with st.spinner(f"Processing '{uploaded_file.name}'..."):
            upload_id = str(uuid.uuid4())

            # Save file temporarily to disk for processing
            storage_path = "./storage"
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)
            file_path = os.path.join(storage_path, f"{upload_id}_{uploaded_file.name}")

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())


            # --- Ingestion Pipeline ---
            try:
                # 1. Record the upload in the database
                new_upload = db.Upload(id=upload_id, filename =uploaded_file.name)
                DB_SESSION.add(new_upload)
                DB_SESSION.commit()

                # 2. Extract text
                if uploaded_file.name.lower().endswith(".pdf"):
                    text = pdf_loader.extract_text_from_pdf(open(file_path, "rb").read())
                else:
                    text = text_loader.extract_text_from_txt(open(file_path, "rb").read())

                # 3. Chunk text
                chunks = chunking.chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

                # 4. Embed and upsert chunks
                if chunks:
                    vectorstore.upsert_chunks(upload_id, uploaded_file.name, chunks)
                    st.toast(f" Successfully ingested '{uploaded_file.name}")
                else:
                    st.warnings(f"No text chunks were extracted from '{uploaded_file.name}'.")
                
                refresh_uploads()
            
            except Exception as e:
                st.error(f'An error occured during ingestion: {e}')
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)

    st.divider()

    # Document List
    st.subheader("Uploaded Documents")
    refresh_uploads_button = st.button("Refresh List 🔄")
    if refresh_uploads_button:
        refresh_uploads()

    if not st.session_state.uploaded_files:
        st.info("No documents uploaded yet.")
    else:
        for upload in st.session_state.uploaded_files:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"📄 {upload.filename}")
            with col2:
                if st.button("🗑️", key=f"del_{upload.id}", help=f"Delete {upload.filename}"):
                    delete_document(upload.id, upload.filename)

#  --- Main Chat Interface ---
st.title(" Knowledge as a Service (KaaS)")
st.markdown("Ask questions about your uploaded documents.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                # 1. Retrieve relevant chunks
                retrieved_docs = retrieval.retrieve_relevant_chunks(prompt, k=7)

                if not retrieved_docs:
                    full_response = "I couldn't find any relevant information in your documents to answer that question."
                else:
                    # 2. Generate an answer
                    answer = generation.generate_answer(prompt, retrieved_docs)

                    # 3. Format the response with sources
                    full_response = answer
                    full_response += "\n\n**Sources:**\n"

                    # Only show top 3 sources in the UI
                    sources_to_show = retrieved_docs[:3]

                    for doc in sources_to_show:
                        filename = doc.metadata.get("filename", "N/A")
                        chunk_index = doc.metadata.get("chunk_index", "N/A")
                        full_response += f"\n- **{filename}** (chunk{chunk_index})\n"
                    
                message_placeholder.markdown(full_response)

            except Exception as e:
                full_response = f"An error occured: {e}"
                message_placeholder.error(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Initial page load - refresh document list 
if not st.session_state.uploaded_files:
    refresh_uploads()

