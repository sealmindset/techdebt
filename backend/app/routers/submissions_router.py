import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.permissions import require_permission
from app.models.submission import Submission
from app.schemas.auth import UserInfo
from app.schemas.submission import SubmissionCreate, SubmissionOut, SubmissionUpdate

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


def _submission_to_out(sub: Submission) -> SubmissionOut:
    """Convert Submission model to SubmissionOut schema."""
    return SubmissionOut(
        id=sub.id,
        app_name=sub.app_name,
        vendor=sub.vendor,
        department=sub.department,
        submitted_by=sub.submitted_by,
        submitter_name=sub.submitter.display_name if sub.submitter else None,
        usage_frequency=sub.usage_frequency,
        business_justification=sub.business_justification,
        user_count_estimate=sub.user_count_estimate,
        annual_cost_estimate=sub.annual_cost_estimate,
        status=sub.status,
        matched_application_id=sub.matched_application_id,
        created_at=sub.created_at,
        updated_at=sub.updated_at,
    )


@router.get("/", response_model=list[SubmissionOut])
async def list_submissions(
    current_user: UserInfo = Depends(require_permission("submissions", "read")),
    db: AsyncSession = Depends(get_db),
):
    """List all voluntary submissions."""
    result = await db.execute(
        select(Submission).order_by(Submission.created_at.desc())
    )
    subs = result.scalars().all()
    return [_submission_to_out(s) for s in subs]


@router.post("/", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def create_submission(
    data: SubmissionCreate,
    current_user: UserInfo = Depends(require_permission("submissions", "create")),
    db: AsyncSession = Depends(get_db),
):
    """Create a voluntary app submission from an end user."""
    sub = Submission(
        **data.model_dump(),
        submitted_by=uuid.UUID(current_user.sub),
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return _submission_to_out(sub)
