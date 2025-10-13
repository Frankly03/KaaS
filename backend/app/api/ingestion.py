import uuid
import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import db
from ..services import pdf_loader, text_loader, chunking, embeddings, vectorstore
from ..config import settings

router = APIRouter()

# --- Ingestion Pipeline ---

def ingest_document(file_path: str, filename: str, upload_id: str):
    """
    The core ingestion pipeline that runs in the background.
    1. Reads file content.
    2. Extracts text.
    3. Chunks text.
    4. Computes embeddings.
    5. Upserts into the vector store.
    """

    try:
        print(f"Starting ingestion for {filename} (upload_id: {upload_id})")
        
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        # 1. Extract text based on file type
        if filename.lower().endswith(".pdf"):
            text = pdf_loader.extract_text_from_pdf(file_bytes)
        elif filename.lower().endswith(".txt"):
            text = text_loader.extract_text_from_txt(file_bytes)
        else:
            raise ValueError("Unsupported file type")
        
        # 2. Chunk text
        chunks = chunking.chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

        # 3. Embed and upsert chunks
        if chunks:
            vectorstore.upsert_chunks(upload_id, filename, chunks)
            print(f"Successfully ingested {len(chunks)} chunks for {filename}.")
        else:
            print(f"No texts chunks extracted from {filename}")

    except Exception as e:
        print(f"Error during ingestion for {filename}: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed temporary file: {file_path}")
    

@router.post("/upload", status_code=202, tags=["Ingestion"])
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db_session: Session = Depends(db.get_db)
):
    """
    Uploads a PDF or TXT file, saves it, and schedules it for background processing.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")
    
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .pdf or .txt file.")
    
    upload_id = str(uuid.uuid4())
 
    # Save file temporarily to disk for processing
    storage_path = "./storage"
    file_path = os.path.join(storage_path, f"{upload_id}_{file.filename}")

    with open(file_path, 'wb') as buffer:
        buffer.write(await file.read()) 

    # Record the upload in the database
    new_upload = db.Upload(id=upload_id, filename=file.filename)
    db_session.add(new_upload)

    audit_log = db.AuditLog(upload_id=upload_id, event_type="upload")
    db_session.add(audit_log)

    db_session.commit()
    db_session.refresh(new_upload)

    # Schedule the background task
    background_tasks.add_task(ingest_document, file_path, file.filename, upload_id)


    # Note: We can't get chunk_count here as it's processed in the background.
    # We return an immediate response to the client.
    return {
        "message": "File upload accepted and is beging processed in the background.",
        "upload_id": new_upload.id,
        "filename": new_upload.filename
    }

@router.post("/reindex/{upload_id}", status_code=202, tags=["Ingestion"])
async def reindex_file(
    upload_id: str,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(db.get_db)
):
    """
    Re-indexes a previously uploaded document. This involves deleting existing
    vectors and re-processing the file from storage.
    """
    upload = db_session.query(db.Upload).filter(db.Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload ID not found.")
    
    # 1. Delete existing vectors for this upload_id
    vectorstore.delete_by_upload_id(upload_id)

    # 2. Find the original file
    audit_log = db.AuditLog(upload_id, event_type="reindex")
    db_session.add(audit_log)
    db_session.commit()

    raise HTTPException(
        status_code=501,
        detail="Re-indexing from storage is not implemented in this MVP, as original files are deleted after ingestion. Please re-upload"
    )