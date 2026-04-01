import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.permissions import require_permission
from app.models.application import Application
from app.models.recommendation import Recommendation
from app.schemas.auth import UserInfo
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationOut,
    RecommendationUpdate,
)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _rec_to_out(rec: Recommendation) -> RecommendationOut:
    """Convert Recommendation model to RecommendationOut schema."""
    return RecommendationOut(
        id=rec.id,
        application_id=rec.application_id,
        application_name=rec.application.name if rec.application else None,
        recommendation_type=rec.recommendation_type,
        confidence_score=rec.confidence_score,
        reasoning=rec.reasoning,
        cost_savings_estimate=rec.cost_savings_estimate,
        alternative_app=rec.alternative_app,
        evidence=rec.evidence,
        status=rec.status,
        created_by=rec.created_by,
        reviewed_by=rec.reviewed_by,
        reviewer_name=rec.reviewer.display_name if rec.reviewer else None,
        reviewed_at=rec.reviewed_at,
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


@router.get("/", response_model=list[RecommendationOut])
async def list_recommendations(
    recommendation_type: str | None = Query(None, alias="type"),
    status_filter: str | None = Query(None, alias="status"),
    application_id: uuid.UUID | None = Query(None),
    current_user: UserInfo = Depends(require_permission("recommendations", "read")),
    db: AsyncSession = Depends(get_db),
):
    """List all recommendations with optional filters."""
    stmt = (
        select(Recommendation)
        .options(selectinload(Recommendation.application))
        .order_by(Recommendation.created_at.desc())
    )

    if recommendation_type:
        stmt = stmt.where(Recommendation.recommendation_type == recommendation_type)
    if status_filter:
        stmt = stmt.where(Recommendation.status == status_filter)
    if application_id:
        stmt = stmt.where(Recommendation.application_id == application_id)

    result = await db.execute(stmt)
    recs = result.scalars().all()
    return [_rec_to_out(r) for r in recs]


@router.get("/{rec_id}", response_model=RecommendationOut)
async def get_recommendation(
    rec_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("recommendations", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single recommendation."""
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.id == rec_id)
        .options(selectinload(Recommendation.application))
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )
    return _rec_to_out(rec)


@router.post("/", response_model=RecommendationOut, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    data: RecommendationCreate,
    current_user: UserInfo = Depends(require_permission("recommendations", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new recommendation for an application."""
    # Verify application exists
    app_result = await db.execute(
        select(Application).where(Application.id == data.application_id)
    )
    if not app_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    rec = Recommendation(**data.model_dump())
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return _rec_to_out(rec)


@router.put("/{rec_id}", response_model=RecommendationOut)
async def update_recommendation(
    rec_id: uuid.UUID,
    data: RecommendationUpdate,
    current_user: UserInfo = Depends(require_permission("recommendations", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update a recommendation's status or review details."""
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == rec_id)
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rec, field, value)

    await db.commit()
    await db.refresh(rec)
    return _rec_to_out(rec)
