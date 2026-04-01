import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.permissions import require_permission
from app.models.application import Application
from app.models.decision import Decision
from app.models.recommendation import Recommendation
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.schemas.auth import UserInfo
from app.schemas.decision import DecisionOut
from app.schemas.recommendation import RecommendationOut

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _app_to_out(app: Application) -> ApplicationOut:
    """Convert Application model to ApplicationOut schema with computed fields."""
    # Calculate potential savings: unused licenses * cost_per_license
    potential_savings = None
    if (
        app.total_licenses is not None
        and app.active_users is not None
        and app.cost_per_license is not None
    ):
        unused = app.total_licenses - app.active_users
        if unused > 0:
            potential_savings = unused * app.cost_per_license

    return ApplicationOut(
        id=app.id,
        name=app.name,
        vendor=app.vendor,
        category=app.category,
        description=app.description,
        app_type=app.app_type,
        status=app.status,
        annual_cost=app.annual_cost,
        cost_per_license=app.cost_per_license,
        total_licenses=app.total_licenses,
        active_users=app.active_users,
        adoption_rate=app.adoption_rate,
        last_login_date=app.last_login_date,
        contract_start=app.contract_start,
        contract_end=app.contract_end,
        department=app.department,
        data_source=app.data_source,
        risk_score=app.risk_score,
        compliance_status=app.compliance_status,
        owner_id=app.owner_id,
        owner_name=app.owner.display_name if app.owner else None,
        potential_savings=potential_savings,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


@router.get("/", response_model=list[ApplicationOut])
async def list_applications(
    category: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    department: str | None = Query(None),
    data_source: str | None = Query(None),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: UserInfo = Depends(require_permission("applications", "read")),
    db: AsyncSession = Depends(get_db),
):
    """List all applications with optional filters, sorting, and pagination."""
    stmt = select(Application)

    if category:
        stmt = stmt.where(Application.category == category)
    if status_filter:
        stmt = stmt.where(Application.status == status_filter)
    if department:
        stmt = stmt.where(Application.department == department)
    if data_source:
        stmt = stmt.where(Application.data_source == data_source)

    # Sorting
    sort_column = getattr(Application, sort_by, Application.name)
    if sort_order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    apps = result.scalars().all()
    return [_app_to_out(a) for a in apps]


@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("applications", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get a single application with recommendations and decisions."""
    stmt = (
        select(Application)
        .where(Application.id == app_id)
        .options(
            selectinload(Application.recommendations),
            selectinload(Application.decisions),
        )
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return _app_to_out(app)


@router.get("/{app_id}/recommendations", response_model=list[RecommendationOut])
async def get_application_recommendations(
    app_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("recommendations", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get all recommendations for a specific application."""
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.application_id == app_id)
        .order_by(Recommendation.created_at.desc())
    )
    recs = result.scalars().all()
    return [
        RecommendationOut(
            id=r.id,
            application_id=r.application_id,
            recommendation_type=r.recommendation_type,
            confidence_score=r.confidence_score,
            reasoning=r.reasoning,
            cost_savings_estimate=r.cost_savings_estimate,
            alternative_app=r.alternative_app,
            evidence=r.evidence,
            status=r.status,
            created_by=r.created_by,
            reviewed_by=r.reviewed_by,
            reviewer_name=r.reviewer.display_name if r.reviewer else None,
            reviewed_at=r.reviewed_at,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in recs
    ]


@router.get("/{app_id}/decisions", response_model=list[DecisionOut])
async def get_application_decisions(
    app_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("decisions", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Get all decisions for a specific application."""
    result = await db.execute(
        select(Decision)
        .where(Decision.application_id == app_id)
        .order_by(Decision.created_at.desc())
    )
    decisions = result.scalars().all()
    return [
        DecisionOut(
            id=d.id,
            application_id=d.application_id,
            recommendation_id=d.recommendation_id,
            decision_type=d.decision_type,
            justification=d.justification,
            submitted_by=d.submitted_by,
            submitter_name=d.submitter.display_name if d.submitter else None,
            status=d.status,
            reviewer_id=d.reviewer_id,
            reviewer_name=d.reviewer.display_name if d.reviewer else None,
            reviewed_at=d.reviewed_at,
            review_notes=d.review_notes,
            target_date=d.target_date,
            cost_impact=d.cost_impact,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in decisions
    ]


@router.post("/", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    current_user: UserInfo = Depends(require_permission("applications", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new application."""
    existing = await db.execute(
        select(Application).where(Application.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application with this name already exists",
        )

    app = Application(**data.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return _app_to_out(app)


@router.put("/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: uuid.UUID,
    data: ApplicationUpdate,
    current_user: UserInfo = Depends(require_permission("applications", "update")),
    db: AsyncSession = Depends(get_db),
):
    """Update an application's details."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    await db.commit()
    await db.refresh(app)
    return _app_to_out(app)


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: uuid.UUID,
    current_user: UserInfo = Depends(require_permission("applications", "delete")),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an application by setting status to 'decommissioned'."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    app.status = "decommissioned"
    await db.commit()
