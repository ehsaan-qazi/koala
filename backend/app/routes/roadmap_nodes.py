"""Roadmap node routes — CRUD + confirm for course assessment items."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.course import Course
from app.models.roadmap_node import RoadmapNode
from app.schemas.roadmap_node import (
    RoadmapNodeCreate,
    RoadmapNodeUpdate,
    RoadmapNodeResponse,
)
from app.schemas.roadmap_node import ALLOWED_NODE_TYPE_VALUES

router = APIRouter(prefix="/roadmap-nodes", tags=["Roadmap Nodes"])


def _validate_node_type(node_type: str) -> str:
    if node_type in ALLOWED_NODE_TYPE_VALUES:
        return node_type
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid node_type. Allowed: {', '.join(sorted(ALLOWED_NODE_TYPE_VALUES))}",
    )


def _recompute_placeholder(node: RoadmapNode) -> None:
    """A node is a placeholder until its key assessment fields are filled."""
    node.is_placeholder = node.deadline is None or node.weight_percent is None


@router.get("/courses/{course_id}", response_model=List[RoadmapNodeResponse])
async def list_course_roadmap_nodes(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all roadmap nodes for a course (newest first)."""
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    nodes_result = await db.execute(
        select(RoadmapNode)
        .where(RoadmapNode.course_id == course_id, RoadmapNode.user_id == current_user.id)
        .order_by(RoadmapNode.created_at.asc())
    )
    return nodes_result.scalars().all()


@router.post("/courses/{course_id}", response_model=RoadmapNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap_node(
    course_id: int,
    node_in: RoadmapNodeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually create a roadmap node (auto-confirmed)."""
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    node_type = _validate_node_type(node_in.node_type)
    node = RoadmapNode(
        course_id=course_id,
        user_id=current_user.id,
        title=node_in.title,
        node_type=node_type,
        deadline=node_in.deadline,
        weight_percent=node_in.weight_percent,
        estimated_hours=node_in.estimated_hours,
        status=node_in.status,
        is_confirmed=True,  # manually created = already confirmed
    )
    _recompute_placeholder(node)
    db.add(node)
    await db.flush()
    await db.refresh(node)
    return node


@router.get("/{node_id}", response_model=RoadmapNodeResponse)
async def get_roadmap_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RoadmapNode).where(RoadmapNode.id == node_id, RoadmapNode.user_id == current_user.id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")
    return node


@router.put("/{node_id}", response_model=RoadmapNodeResponse)
async def update_roadmap_node(
    node_id: int,
    node_in: RoadmapNodeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RoadmapNode).where(RoadmapNode.id == node_id, RoadmapNode.user_id == current_user.id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    update_data = node_in.model_dump(exclude_unset=True)
    if "node_type" in update_data and update_data["node_type"] is not None:
        update_data["node_type"] = _validate_node_type(update_data["node_type"])

    for key, value in update_data.items():
        setattr(node, key, value)

    _recompute_placeholder(node)
    await db.flush()
    await db.refresh(node)
    return node


@router.post("/{node_id}/confirm", response_model=RoadmapNodeResponse)
async def confirm_roadmap_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a roadmap node as confirmed by the student."""
    result = await db.execute(
        select(RoadmapNode).where(RoadmapNode.id == node_id, RoadmapNode.user_id == current_user.id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")

    node.is_confirmed = True
    _recompute_placeholder(node)  # if user filled deadline/weight, drop placeholder flag
    await db.flush()
    await db.refresh(node)
    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap_node(
    node_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RoadmapNode).where(RoadmapNode.id == node_id, RoadmapNode.user_id == current_user.id)
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Roadmap node not found")
    await db.delete(node)
