from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from celery import Celery

from core.database.database import get_db
from core.config.settings import settings
from apps.auth.utils import get_current_user
from apps.auth.models import User
from .models import Document, Summary
from .schemas import (
    DocumentCreate,
    DocumentInDB,
    DocumentUpdate,
    SummaryInDB,
    SummarizationRequest,
    SummarizationResponse
)
from .utils import summarize_text

router = APIRouter()
celery = Celery(
    'summarization',
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND)
)

@router.post("/documents", response_model=DocumentInDB)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DocumentInDB:
    db_document = Document(
        title=document.title,
        content=document.content,
        user_id=current_user.id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/documents", response_model=List[DocumentInDB])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[DocumentInDB]:
    documents = db.query(Document)\
        .filter(Document.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return documents

@router.post("/summarize", response_model=SummarizationResponse)
async def summarize(
    request: SummarizationRequest,
    current_user: User = Depends(get_current_user)
) -> SummarizationResponse:
    try:
        result = summarize_text(
            request.text,
            max_length=request.max_length,
            min_length=request.min_length
        )
        return SummarizationResponse(
            summary=result["summary"],
            original_length=result["original_length"],
            summary_length=result["summary_length"],
            compression_ratio=result["compression_ratio"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/documents/{document_id}/summarize", response_model=SummaryInDB)
async def summarize_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SummaryInDB:
    document = db.query(Document)\
        .filter(Document.id == document_id)\
        .filter(Document.user_id == current_user.id)\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        result = summarize_text(document.content)
        summary = Summary(
            document_id=document.id,
            content=result["summary"],
            length=result["summary_length"]
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 