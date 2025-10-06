from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .. import db
from ..services import retrieval, generation

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    k: int = 7

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]
    audit_id: int

@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_document(
    request: QueryRequest,
    db_session: Session = Depends(db.get_db)
):
    """
    Asks a question about the uploaded documents.
    Retrieves relevant text chunks and generates a cited answer.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        # Retrieve relevant chunks from the vector store
        retrieved_docs = retrieval.retrieve_relevant_chunks(request.question, k=request.k)

        if not retrieved_docs:
            answer = "I couldn't find any relevant information in the uploaded document."
            sources = []
        else:
            # 2. Generate an answer usign the retrieved context
            answer = generation.generate_answer(request.question, retrieved_docs)
            all_sources = [
                {
                    "filename": doc.metadata.get("filename"),
                    "chunk_index": doc.metadata.get("chunk_index"),
                    "snippet": doc.page_content,
                    "char_start": doc.metadata.get("char_start"),
                    "char_end": doc.metadata.get("char_end")
                } for doc in retrieved_docs
            ]

            # Only return the top 3 sources to the frontend to avoid clutter
            sources = all_sources[:3]

        
        # 3. Long the query and response to the audit log
        audit_log = db.AuditLog(
            event_type="query",
            query_text=request.question,
            response_text=answer
        )
        db_session.add(audit_log)
        db_session.commit()
        db_session.refresh(audit_log)

        return QueryResponse(
            query=request.question,
            answer=answer,
            sources=sources,
            audit_id=audit_log.id
        )
    except Exception as e:
        print(f"Error during query processing: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occured: {e}")