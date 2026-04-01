import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.permissions import require_permission
from app.models.application import Application
from app.models.decision import Decision
from app.schemas.auth import UserInfo
from app.schemas.decision import DecisionCreate, DecisionOut, DecisionUpdate

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


def _decision_to_out(decision: Decision) -> DecisionOut:
    """Convert Decision model to DecisionOut schema."""
    return DecisionOut(
        id=decision.id,
        application_id=decision.application_id,
        application_name=decision.application.name if decision.application else None,
        recommendation_id=decision.recommendation_id,
        decision_type=decision.decision_type,
        justification=decision.justification,
        submitted_by=decision.submitted_by,
        submitter_name=decision.submitter.display_name if decision.submitter else None,
        status=decision.status,
        reviewer_id=decision.reviewer_id,
        reviewer_name=decision.reviewer.display_name if decision.reviewer else None,
        reviewed_at=decision.reviewed_at,
        review_notes=decision.review_notes,
        target_date=decision.target_date,
        cost_impact=decision.cost_impact,
        created_at=decision.created_at,
        updated_at=decision.updated_at,
    )


@router.get("/", response_model=list[DecisionOut])
async def list_decisions(
    status_filter: str | None = Query(None, alias="status"),
    decision_type: str | None = Query(None),
    current_user: UserInfo = Depends(require_permission("decisions", "read")),
    db: AsyncSession = Depends(get_db),
):
    """List all decisions with optional filters."""
    stmt = (
        select(Decision)
        .options(selectinload(Decision.application))
        .order_by(Decision.created_at.desc())
    )

    if status_filter:
        stmt = stmt.where(Decision.status == status_filter)
    if decision_type:
        stmt = stmt.where(Decision.decision_type == decision_type)

    result = await db.execute(stmt)
    decisions = result.scalars().all()
    return [_decision_to_out(d) for d in decisions]


@router.get("/{decision_id}", response_model=DecisionOut)
async def get_decision(
    decision_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("decisions", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single decision."""
    result = await db.execute(
        select(Decision)
        .where(Decision.id == decision_id)
        .options(selectinload(Decision.application))
    )
    decision = result.scalar_one_or_none()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )
    return _decision_to_out(decision)


@router.post("/", response_model=DecisionOut, status_code=status.HTTP_201_CREATED)
async def create_decision(
    data: DecisionCreate,
    current_user: UserInfo = Depends(require_permission("decisions", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new decision with justification."""
    # Verify application exists
    app_result = await db.execute(
        select(Application).where(Application.id == data.application_id)
    )
    if not app_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    decision = Decision(
        **data.model_dump(),
        submitted_by=uuid.UUID(current_user.sub),
    )
    db.add(decision)
    await db.commit()
    await db.refresh(decision)
    return _decision_to_out(decision)


@router.put("/{decision_id}", response_model=DecisionOut)
async def update_decision(
    decision_id: uuid.UUID,
    data: DecisionUpdate,
    current_user: UserInfo = Depends(require_permission("decisions", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update a decision -- approve, reject, or modify."""
    result = await db.execute(
        select(Decision).where(Decision.id == decision_id)
    )
    decision = result.scalar_one_or_none()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    # If status is changing to approved/rejected, record reviewer info
    if "status" in update_data and update_data["status"] in ("approved", "rejected"):
        decision.reviewer_id = uuid.UUID(current_user.sub)
        decision.reviewed_at = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(decision, field, value)

    await db.commit()
    await db.refresh(decision)
    return _decision_to_out(decision)
