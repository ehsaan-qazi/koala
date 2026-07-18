"""Document routes — upload, list, delete syllabus files + trigger AI extraction."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.course import Course
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListItem
from app.services import storage_service
from app.services.extraction_service import extract_topics_for_document
from app.config import settings

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
    "application/vnd.ms-powerpoint",  # ppt
}


@router.post("/courses/{course_id}/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    course_id: int,
    file: UploadFile = File(...),
    doc_type: str = Form(default="syllabus"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document to a course. Stores in Cloudflare R2 with full metadata."""
    # Verify course ownership
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Enforce upload limits based on user plan
    max_uploads = settings.pro_upload_limit if current_user.plan == "pro" else settings.free_upload_limit
    if course.doc_upload_count >= max_uploads:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Upload limit reached ({max_uploads} documents per course on {current_user.plan} plan)",
        )

    # Read file bytes
    file_data = await file.read()

    # Enforce file size limits
    max_size_mb = settings.pro_max_file_size_mb if current_user.plan == "pro" else settings.free_max_file_size_mb
    if len(file_data) > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {max_size_mb} MB limit for {current_user.plan} plan",
        )

    # Compute SHA-256 for integrity and duplicate detection
    sha256 = storage_service.compute_sha256(file_data)

    # Check for duplicate uploads (same user, same hash)
    existing = await db.execute(
        select(Document).where(Document.user_id == current_user.id, Document.sha256 == sha256)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This file has already been uploaded",
        )

    # Generate R2 key and upload
    r2_key = storage_service.generate_r2_key(current_user.id, course_id, file.filename or "upload.pdf")
    storage_service.upload_file(file_data, r2_key, content_type=file.content_type or "application/pdf")

    # Create database record with enriched metadata
    document = Document(
        course_id=course_id,
        user_id=current_user.id,
        doc_type=doc_type,
        original_filename=file.filename or "upload.pdf",
        r2_key=r2_key,
        mime_type=file.content_type,
        size_bytes=len(file_data),
        sha256=sha256,
    )
    db.add(document)

    # Increment upload count
    course.doc_upload_count += 1

    await db.flush()
    await db.refresh(document)
    return document


@router.get("/courses/{course_id}", response_model=List[DocumentListItem])
async def list_course_documents(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for a course."""
    # Verify course ownership
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    result = await db.execute(
        select(Document)
        .where(Document.course_id == course_id, Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
    )
    return result.scalars().all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document from R2 and the database."""
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from R2
    try:
        storage_service.delete_file(document.r2_key)
    except Exception:
        pass  # If R2 delete fails, still remove DB record

    # Decrement upload count on course
    course_result = await db.execute(select(Course).where(Course.id == document.course_id))
    course = course_result.scalar_one_or_none()
    if course and course.doc_upload_count > 0:
        course.doc_upload_count -= 1

    await db.delete(document)


@router.post("/{document_id}/extract", response_model=dict)
async def trigger_extraction(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI extraction of topics from a document."""
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.processing_status == "processed":
        raise HTTPException(status_code=400, detail="Document has already been processed")

    topics = await extract_topics_for_document(document, db)

    return {
        "status": document.processing_status,
        "topics_extracted": len(topics),
        "topics": [t.title for t in topics],
    }
