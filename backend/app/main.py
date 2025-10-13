import os
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List

from .api import ingestion, query
from . import db
from .services import vectorstore
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    db.init_db()
    vectorstore.init_vectorstore()
    
    storage_path = './storage'
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
        
    yield
    print("Shutting down...")

app = FastAPI(
    title="KnowledgeOps as a Service (KaaS)",
    description="API for uploading documents and querying them using RAG.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router)
app.include_router(query.router)

# --- Document Listing, Deletion, and Reset Endpoints ---
class DocumentResponse(BaseModel):
    id: str
    filename: str
    created_at: datetime
    class Config:
        orm_mode = True

@app.get("/documents", tags=["Admin"], response_model=List[DocumentResponse])
def get_documents(db_session: Session = Depends(db.get_db)):
    """Lists all uploaded documents from the database."""
    uploads = db_session.query(db.Upload).order_by(db.Upload.created_at.desc()).all()
    return uploads

@app.delete("/documents/{upload_id}", status_code=200, tags=["Admin"])
def delete_document(upload_id: str, db_session: Session = Depends(db.get_db)):
    """Deletes a specific document from all databases (SQLite and Chroma)."""
    upload = db_session.query(db.Upload).filter(db.Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload ID not found.")
    
    try:
        # Delete from ChromaDB
        vectorstore.delete_by_upload_id(upload_id)
        
        # Delete from SQLite
        db_session.delete(upload)
        db_session.commit()
        
        return {"status": "ok", "message": f"Document '{upload.filename}' deleted."}
    except Exception as e:
        db_session.rollback()
        print(f"Error during document deletion: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document.")


@app.post("/reset", status_code=200, tags=["Admin"])
def reset_system(db_session: Session = Depends(db.get_db)):
    """Deletes all data from all databases (SQLite and Chroma)."""
    try:
        # Delete from SQLite
        db_session.query(db.AuditLog).delete()
        db_session.query(db.Upload).delete()
        db_session.commit()
        print("All records deleted from SQLite database.")

        # Delete from Chroma
        vectorstore.reset_vectorstore()

        return {"status": "ok", "message": "System has been reset."}
    except Exception as e:
        db_session.rollback()
        print(f"Error during system reset: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset system.")

@app.get("/", tags=["Health Check"])
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Welcome to KaaS API!"}

