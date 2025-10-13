from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
from .config import settings

# Use a file-based SQLite database
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    audit_logs = relationship("AuditLog", back_populates="upload")

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(String, ForeignKey("uploads.id"), nullable=True)
    event_type = Column(String)
    query_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    upload = relationship("Upload", back_populates="audit_logs")

def init_db():
    """Initialize the database and creates tables if they don't exists."""
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()