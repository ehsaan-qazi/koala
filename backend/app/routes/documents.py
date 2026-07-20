"""Document routes — upload, list, delete syllabus files + trigger AI extraction."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db, async_session
from app.middleware.auth import get_current_user
from app.middleware.tier_gate import require_pro, check_upload_limit, get_file_size_limit_bytes
from app.models.user import User
from app.models.course import Course
from app.models.document import Document
from app.models.roadmap_node import RoadmapNode
from app.schemas.document import DocumentResponse, DocumentListItem
from app.services import storage_service
from app.services.extraction_service import extract_topics_for_document
from app.services.roadmap_extraction import extract_roadmap_for_document

logger = logging.getLogger(__name__)

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
    check_upload_limit(course, current_user)

    # Enforce file size limits
    max_size_bytes = get_file_size_limit_bytes(current_user)

    # Read file bytes
    file_data = await file.read()

    # Validate file size
    if len(file_data) > max_size_bytes:
        max_size_mb = max_size_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {max_size_mb} MB limit for {current_user.plan} plan",
        )

    # Validate doc_type
    allowed_doc_types = {"syllabus", "clo", "instructor_notes", "slides", "academic_calendar"}
    if doc_type not in allowed_doc_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid doc_type. Allowed: {', '.join(sorted(allowed_doc_types))}",
        )

    # Pro-only document types
    pro_only_types = {"instructor_notes", "slides"}
    if doc_type in pro_only_types and current_user.plan != "pro":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This document type requires a Pro subscription",
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
    try:
        storage_service.upload_file(file_data, r2_key, content_type=file.content_type or "application/pdf")
    except Exception as exc:
        # Surface the real storage error (e.g. R2 SignatureDoesNotMatch) instead
        # of a generic 500 so the client can show the actual cause.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"File storage upload failed: {exc}",
        )

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
    """Trigger AI extraction of topics from a document. Requires Pro plan."""
    require_pro(current_user)

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


async def _run_roadmap_extraction(document_id: int, user_id: int) -> None:
    """Background task: run roadmap extraction with its own DB session."""
    async with async_session() as db:
        try:
            result = await db.execute(
                select(Document).where(Document.id == document_id, Document.user_id == user_id)
            )
            document = result.scalar_one_or_none()
            if not document:
                return
            await extract_roadmap_for_document(document, db)
            await db.commit()
        except Exception:
            await db.rollback()
            logger.exception("Background roadmap extraction failed for document %d", document_id)


@router.post("/{document_id}/extract-roadmap", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def trigger_roadmap_extraction(
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI extraction of the assessment roadmap from a syllabus.

    This is the Phase 2 core feature and is available on the FREE tier
    (subject to the per-course upload limit). Extraction runs in the
    background; poll GET /documents/{id}/extraction-status for progress.
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.processing_status == "processed":
        raise HTTPException(status_code=400, detail="Document has already been processed")

    document.processing_status = "processing"
    await db.flush()

    background_tasks.add_task(_run_roadmap_extraction, document.id, current_user.id)

    return {
        "status": "processing",
        "document_id": document.id,
        "message": "Roadmap extraction started",
    }


@router.get("/{document_id}/extraction-status", response_model=dict)
async def extraction_status(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Poll the extraction status of a document (processing | processed | failed)."""
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    count_result = await db.execute(
        select(func.count(RoadmapNode.id)).where(
            RoadmapNode.source_document_id == document_id,
            RoadmapNode.user_id == current_user.id,
        )
    )
    node_count = count_result.scalar() or 0

    return {
        "status": document.processing_status,
        "error_message": document.error_message,
        "nodes_extracted": node_count,
    }
