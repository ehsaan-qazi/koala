"""Topic routes — CRUD for course topics and completion toggles."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.course import Course
from app.models.topic import Topic
from app.models.topic_completion import TopicCompletion
from app.schemas.topic import TopicCreate, TopicUpdate, TopicToggle, TopicResponse, TopicWithCompletion

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("/courses/{course_id}", response_model=List[TopicWithCompletion])
async def list_course_topics(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all topics for a course, including completion state."""
    # Verify course ownership
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    # Get all topics for this course
    topics_result = await db.execute(
        select(Topic)
        .where(Topic.course_id == course_id)
        .order_by(Topic.order_index)
    )
    topics = topics_result.scalars().all()

    # Get completions for current user
    completions_result = await db.execute(
        select(TopicCompletion).where(
            TopicCompletion.user_id == current_user.id,
            TopicCompletion.topic_id.in_([t.id for t in topics]) if topics else False,
        )
    )
    completions = {tc.topic_id: tc for tc in completions_result.scalars().all()} if topics else {}

    # Merge topics with completion state
    result_list = []
    for topic in topics:
        tc = completions.get(topic.id)
        result_list.append(TopicWithCompletion(
            id=topic.id,
            course_id=topic.course_id,
            title=topic.title,
            order_index=topic.order_index,
            is_confirmed=topic.is_confirmed,
            source_document_id=topic.source_document_id,
            linked_node_id=topic.linked_node_id,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
            is_completed=tc.is_completed if tc else False,
            confidence_rating=tc.confidence_rating if tc else None,
        ))

    return result_list


@router.post("/courses/{course_id}", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    course_id: int,
    topic_in: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually create a topic for a course."""
    # Verify course ownership
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    topic = Topic(
        course_id=course_id,
        user_id=current_user.id,
        title=topic_in.title,
        order_index=topic_in.order_index,
        is_confirmed=True,  # Manually created topics are auto-confirmed
    )
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    return topic


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a topic's title or order."""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id, Topic.user_id == current_user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    update_data = topic_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(topic, key, value)

    await db.flush()
    await db.refresh(topic)
    return topic


@router.patch("/{topic_id}/toggle", response_model=TopicWithCompletion)
async def toggle_topic_completion(
    topic_id: int,
    toggle_in: TopicToggle,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a topic's completion state for the current user."""
    # Verify topic exists and belongs to user
    topic_result = await db.execute(
        select(Topic).where(Topic.id == topic_id, Topic.user_id == current_user.id)
    )
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Find or create completion record
    comp_result = await db.execute(
        select(TopicCompletion).where(
            TopicCompletion.topic_id == topic_id,
            TopicCompletion.user_id == current_user.id,
        )
    )
    completion = comp_result.scalar_one_or_none()

    if completion:
        completion.is_completed = toggle_in.is_completed
        if toggle_in.confidence_rating is not None:
            completion.confidence_rating = toggle_in.confidence_rating
    else:
        from datetime import datetime, timezone
        completion = TopicCompletion(
            topic_id=topic_id,
            user_id=current_user.id,
            is_completed=toggle_in.is_completed,
            confidence_rating=toggle_in.confidence_rating,
            completed_at=datetime.now(timezone.utc) if toggle_in.is_completed else None,
        )
        db.add(completion)

    await db.flush()

    return TopicWithCompletion(
        id=topic.id,
        course_id=topic.course_id,
        title=topic.title,
        order_index=topic.order_index,
        is_confirmed=topic.is_confirmed,
        source_document_id=topic.source_document_id,
        linked_node_id=topic.linked_node_id,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        is_completed=completion.is_completed,
        confidence_rating=completion.confidence_rating,
    )


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a topic."""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id, Topic.user_id == current_user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    await db.delete(topic)
