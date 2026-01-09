from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
import os
import shutil
from pathlib import Path
from loguru import logger

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, Document, DocumentChunk
from app.api.auth import get_current_user
from app.services.document_processor import DocumentProcessor

router = APIRouter()


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    created_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Upload and process a document"""
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"File saved: {file_path}")
    
    # Create document record
    document = Document(
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_ext,
        file_size=file_size,
        user_id=current_user.id,
        status="pending"
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Process document asynchronously (in production, use a task queue)
    try:
        document.status = "processing"
        await db.commit()
        
        # Process document
        processor = DocumentProcessor()
        chunks = await processor.process_document(str(file_path), file_ext)
        
        # Get vector store from request state
        vector_store = request.app.state.vector_store
        
        # Add chunks to vector store
        chunk_texts = [chunk['content'] for chunk in chunks]
        chunk_metadatas = [
            {
                **chunk['metadata'],
                'document_id': document.id,
                'user_id': current_user.id
            }
            for chunk in chunks
        ]
        
        vector_ids = await vector_store.add_documents(
            texts=chunk_texts,
            metadatas=chunk_metadatas
        )
        
        # Save chunks to database
        for i, (chunk, vector_id) in enumerate(zip(chunks, vector_ids)):
            db_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk['content'],
                metadata=chunk['metadata'],
                vector_id=vector_id
            )
            db.add(db_chunk)
        
        document.status = "completed"
        from datetime import datetime
        document.processed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(document)
        
        logger.info(f"Document processed successfully: {document.filename}")
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        document.status = "failed"
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        status=document.status,
        created_at=document.created_at.isoformat()
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List all documents for the current user"""
    
    # Get total count
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id)
    )
    all_docs = result.scalars().all()
    total = len(all_docs)
    
    # Get paginated results
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()
    
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                status=doc.status,
                created_at=doc.created_at.isoformat()
            )
            for doc in documents
        ],
        total=total
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID"""
    
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        status=document.status,
        created_at=document.created_at.isoformat()
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Delete a document"""
    
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete from vector store
    result = await db.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )
    chunks = result.scalars().all()
    
    vector_ids = [chunk.vector_id for chunk in chunks if chunk.vector_id]
    
    if vector_ids:
        vector_store = request.app.state.vector_store
        await vector_store.delete_documents(vector_ids)
    
    # Delete file
    try:
        os.remove(document.file_path)
    except Exception as e:
        logger.warning(f"Could not delete file: {str(e)}")
    
    # Delete from database (cascades to chunks)
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}