"""
AI roadmap extraction service — extract assessment items (roadmap nodes) from a
syllabus PDF using Groq.

Pipeline (mirrors extraction_service.py but targets roadmap_nodes):
1. Download PDF from R2
2. Extract text via pypdf
3. Send to Groq via the circuit-breaker router (structured JSON output)
4. Parse the JSON into roadmap nodes
5. Bulk insert RoadmapNode rows linked to the source document

Each extracted node carries:
- node_type   (Assignment | Quiz | Exam | Project | Lab | Other)
- deadline    (ISO 8601 date or null → becomes a placeholder)
- weight_percent (numeric or null → becomes a placeholder)
- extraction_confidence (0.0–1.0 per node)
- is_placeholder / is_confirmed (False until the student confirms)
"""

import io
import json
import logging
from datetime import datetime, timezone

from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.concurrency import run_in_threadpool

from app.models.document import Document
from app.models.roadmap_node import RoadmapNode
from app.services import storage_service
from app.services.groq_router import get_router

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Allowed node types (must match the DB CHECK constraint)
# ──────────────────────────────────────────────────────────────────────────────
ALLOWED_NODE_TYPES = {"Assignment", "Quiz", "Exam", "Project", "Lab", "Other"}

# Normalisation map for common LLM phrasing → canonical node_type
NODE_TYPE_ALIASES = {
    "assignment": "Assignment",
    "assignments": "Assignment",
    "homework": "Assignment",
    "problem set": "Assignment",
    "pset": "Assignment",
    "quiz": "Quiz",
    "quizzes": "Quiz",
    "exam": "Exam",
    "exams": "Exam",
    "midterm": "Exam",
    "midterm exam": "Exam",
    "final": "Exam",
    "final exam": "Exam",
    "test": "Exam",
    "project": "Project",
    "projects": "Project",
    "lab": "Lab",
    "labs": "Lab",
    "laboratory": "Lab",
    "lab report": "Lab",
    "other": "Other",
}

# Max characters sent to the LLM (keeps well within context windows)
MAX_SYLLABUS_CHARS = 25_000


# ──────────────────────────────────────────────────────────────────────────────
# System prompt — structured roadmap extraction
# ──────────────────────────────────────────────────────────────────────────────
ROADMAP_SYSTEM_PROMPT = """You are an academic syllabus parser. Extract the list of graded ASSESSMENT ITEMS (assignments, quizzes, exams, projects, labs) from a syllabus PDF.

Rules:
1. Extract each distinct graded assessment item mentioned in the syllabus.
2. For each item, determine:
   - "title": a short, clear name (e.g. "Midterm Exam", "Project 1", "Homework 3").
   - "node_type": one of "Assignment", "Quiz", "Exam", "Project", "Lab", or "Other".
   - "deadline": the due/exam DATE in ISO 8601 format (YYYY-MM-DD) if stated, else null.
   - "weight_percent": the item's contribution to the final grade as a NUMBER (e.g. 20 for 20%) if stated, else null.
   - "confidence": your confidence (0.0–1.0) in the extracted fields.
3. Split compound items (e.g. "3 assignments worth 10% each") into individual nodes.
4. Never invent dates or weights — if uncertain or not stated, use null (it becomes a placeholder the student must fill).
5. Ignore administrative items (office hours, grading policies text) unless they name a concrete assessment.

Respond ONLY with a JSON object of this exact shape (no markdown fences):
{
  "nodes": [
    {"title": "string", "node_type": "Exam", "deadline": "2026-10-15", "weight_percent": 30, "confidence": 0.9}
  ],
  "warnings": ["string"]
}

If you cannot extract any assessment items, return: {"nodes": [], "warnings": ["reason"]}"""


# ──────────────────────────────────────────────────────────────────────────────
# PDF helpers (shared behaviour with topic extraction)
# ──────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text content from a PDF file."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _parse_deadline(value) -> datetime | None:
    """Parse an ISO 8601 date string into a timezone-aware datetime, or None."""
    if not value:
        return None
    if isinstance(value, (list, dict)):
        return None
    text = str(value).strip()
    if not text:
        return None
    # Normalise a bare date or datetime; handle trailing Z
    try:
        normalised = text.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalised)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        logger.warning("Could not parse deadline %r — treating as placeholder", value)
        return None


def _normalise_node_type(value) -> str:
    """Map free-form LLM node_type text to a canonical allowed value."""
    if not value:
        return "Other"
    key = str(value).strip().lower()
    return NODE_TYPE_ALIASES.get(key, "Other")


def _parse_roadmap_from_response(response_text: str) -> tuple[list[dict], list[str]]:
    """
    Parse the structured JSON roadmap response.

    Returns (nodes, warnings). Handles optional markdown code fences.
    """
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse roadmap LLM response as JSON: %.200s", text)
        return [], ["AI returned an unreadable response"]

    if not isinstance(parsed, dict):
        logger.warning("Roadmap LLM returned non-object JSON: %.200s", text)
        return [], ["AI returned an unexpected response shape"]

    raw_nodes = parsed.get("nodes", [])
    warnings = parsed.get("warnings", []) or []
    if not isinstance(raw_nodes, list):
        return [], warnings + ["AI returned malformed nodes"]

    nodes: list[dict] = []
    for item in raw_nodes:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        confidence = item.get("confidence")
        try:
            confidence = float(confidence) if confidence is not None else None
        except (TypeError, ValueError):
            confidence = None
        if confidence is not None:
            confidence = max(0.0, min(1.0, confidence))

        weight = item.get("weight_percent")
        try:
            weight = float(weight) if weight is not None else None
        except (TypeError, ValueError):
            weight = None

        deadline = _parse_deadline(item.get("deadline"))
        node_type = _normalise_node_type(item.get("node_type"))

        # Placeholder when a key assessment field could not be determined
        is_placeholder = deadline is None or weight is None

        nodes.append({
            "title": title,
            "node_type": node_type,
            "deadline": deadline,
            "weight_percent": weight,
            "extraction_confidence": confidence,
            "is_placeholder": is_placeholder,
        })

    return nodes, warnings


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def call_groq_for_roadmap(syllabus_text: str) -> tuple[list[dict], list[str], str]:
    """
    Send syllabus text to Groq via the circuit-breaker router.

    Returns (nodes, warnings, model_used). Raises RuntimeError if all models fail.
    """
    if len(syllabus_text) > MAX_SYLLABUS_CHARS:
        syllabus_text = syllabus_text[:MAX_SYLLABUS_CHARS] + "\n\n[... truncated for length]"

    messages = [
        {"role": "system", "content": ROADMAP_SYSTEM_PROMPT},
        {"role": "user", "content": f"Extract the assessment items from this syllabus:\n\n{syllabus_text}"},
    ]

    router = get_router()
    response_text, model_used = router.chat(messages=messages, temperature=0.1, max_tokens=3000)

    nodes, warnings = _parse_roadmap_from_response(response_text)
    return nodes, warnings, model_used


async def extract_roadmap_for_document(
    document: Document,
    db: AsyncSession,
) -> list[RoadmapNode]:
    """
    Full roadmap extraction pipeline for a single document:
      1. Download PDF from R2
      2. Extract text via pypdf
      3. Call Groq (with circuit-breaker fallback) for structured roadmap
      4. Insert RoadmapNode rows into the DB, linked to this document

    Updates `document.processing_status` and `document.error_message` in place.
    """
    document.processing_status = "processing"
    await db.flush()

    try:
        # Step 1: Download PDF from R2 (blocking I/O → offload to threadpool)
        pdf_bytes = await run_in_threadpool(storage_service.download_file, document.r2_key)

        # Step 2: Extract text (CPU-bound → offload to threadpool)
        syllabus_text = await run_in_threadpool(extract_text_from_pdf, pdf_bytes)
        if not syllabus_text.strip():
            document.processing_status = "failed"
            document.error_message = "Could not extract any text from the PDF"
            await db.flush()
            return []

        # Step 3: Call Groq with fallback (network-bound → offload to threadpool)
        nodes, warnings, model_used = await run_in_threadpool(call_groq_for_roadmap, syllabus_text)
        logger.info(
            "Extracted %d roadmap nodes from document %d using model %s",
            len(nodes), document.id, model_used,
        )
        if warnings:
            logger.info("Roadmap extraction warnings for document %d: %s", document.id, warnings)

        if not nodes:
            document.processing_status = "failed"
            document.error_message = "AI could not identify any assessment items in this document"
            await db.flush()
            return []

        # Step 4: Bulk insert roadmap nodes
        created_nodes: list[RoadmapNode] = []
        for node in nodes:
            roadmap_node = RoadmapNode(
                course_id=document.course_id,
                user_id=document.user_id,
                source_document_id=document.id,
                title=node["title"],
                node_type=node["node_type"],
                deadline=node["deadline"],
                weight_percent=node["weight_percent"],
                extraction_confidence=node["extraction_confidence"],
                is_placeholder=node["is_placeholder"],
                is_confirmed=False,
                status="Pending",
                estimated_hours=None,
                actual_hours=None,
                confidence_at_creation=None,
            )
            db.add(roadmap_node)
            created_nodes.append(roadmap_node)

        document.processing_status = "processed"
        document.processed_at = datetime.now(timezone.utc)
        document.error_message = None
        await db.flush()

        return created_nodes

    except Exception as exc:
        logger.exception("Roadmap extraction failed for document %d", document.id)
        document.processing_status = "failed"
        document.error_message = str(exc)[:500]
        await db.flush()
        return []
