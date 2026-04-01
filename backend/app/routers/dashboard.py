from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.permissions import require_permission
from app.models.application import Application
from app.models.decision import Decision
from app.models.recommendation import Recommendation
from app.schemas.auth import UserInfo
from app.schemas.dashboard import (
    DashboardStats,
    RecentDecision,
    SavingsOpportunity,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: UserInfo = Depends(require_permission("dashboard", "read")),
    db: AsyncSession = Depends(get_db),
):
    """Return aggregated dashboard statistics."""
    # Total apps (exclude decommissioned)
    total_apps_result = await db.execute(
        select(func.count(Application.id)).where(
            Application.status != "decommissioned"
        )
    )
    total_apps = total_apps_result.scalar() or 0

    # Total spend
    total_spend_result = await db.execute(
        select(func.coalesce(func.sum(Application.annual_cost), 0.0)).where(
            Application.status != "decommissioned"
        )
    )
    total_spend = float(total_spend_result.scalar() or 0.0)

    # Average adoption rate
    avg_adoption_result = await db.execute(
        select(func.avg(Application.adoption_rate)).where(
            Application.adoption_rate.isnot(None),
            Application.status != "decommissioned",
        )
    )
    avg_adoption_rate = float(avg_adoption_result.scalar() or 0.0)

    # Apps by status
    status_rows = await db.execute(
        select(Application.status, func.count(Application.id)).group_by(
            Application.status
        )
    )
    apps_by_status = {row[0]: row[1] for row in status_rows.all()}

    # Apps by category
    category_rows = await db.execute(
        select(Application.category, func.count(Application.id))
        .where(Application.status != "decommissioned")
        .group_by(Application.category)
    )
    apps_by_category = {row[0]: row[1] for row in category_rows.all()}

    # Apps by recommendation type
    rec_rows = await db.execute(
        select(Recommendation.recommendation_type, func.count(Recommendation.id))
        .where(Recommendation.status == "pending")
        .group_by(Recommendation.recommendation_type)
    )
    apps_by_recommendation = {row[0]: row[1] for row in rec_rows.all()}

    # Top savings opportunities -- join with recommendations for richer data
    savings_rows = await db.execute(
        select(
            Application.id,
            Application.name,
            Application.vendor,
            Application.annual_cost,
            (
                (Application.total_licenses - Application.active_users)
                * Application.cost_per_license
            ).label("savings"),
        )
        .where(
            Application.total_licenses.isnot(None),
            Application.active_users.isnot(None),
            Application.cost_per_license.isnot(None),
            Application.total_licenses > Application.active_users,
            Application.status != "decommissioned",
        )
        .order_by(
            (
                (Application.total_licenses - Application.active_users)
                * Application.cost_per_license
            ).desc()
        )
        .limit(10)
    )
    savings_data = savings_rows.all()

    # Get recommendation types for these apps
    app_ids = [row[0] for row in savings_data]
    rec_type_rows = await db.execute(
        select(Recommendation.application_id, Recommendation.recommendation_type)
        .where(
            Recommendation.application_id.in_(app_ids),
            Recommendation.status == "pending",
        )
    )
    rec_type_map = {str(row[0]): row[1] for row in rec_type_rows.all()}

    top_savings_opportunities = [
        SavingsOpportunity(
            id=str(row[0]),
            name=row[1],
            vendor=row[2],
            annual_cost=float(row[3] or 0),
            savings_estimate=float(row[4]),
            recommendation_type=rec_type_map.get(str(row[0])),
        )
        for row in savings_data
    ]

    # Total potential savings
    total_potential_savings = sum(
        s.savings_estimate for s in top_savings_opportunities
    )

    # Recent decisions (last 10)
    recent_rows = await db.execute(
        select(Decision)
        .order_by(Decision.created_at.desc())
        .limit(10)
    )
    decisions = recent_rows.scalars().all()
    recent_decisions = []
    for d in decisions:
        # Get app name
        app_result = await db.execute(
            select(Application.name).where(Application.id == d.application_id)
        )
        app_name = app_result.scalar() or "Unknown"
        recent_decisions.append(
            RecentDecision(
                id=str(d.id),
                application_name=app_name,
                decision_type=d.decision_type,
                status=d.status,
                submitted_by=d.submitter.display_name if d.submitter else None,
                created_at=d.created_at.isoformat() if d.created_at else None,
            )
        )

    return DashboardStats(
        total_apps=total_apps,
        total_spend=total_spend,
        avg_adoption_rate=round(avg_adoption_rate, 1),
        total_potential_savings=total_potential_savings,
        apps_by_status=apps_by_status,
        apps_by_category=apps_by_category,
        recommendations_summary=apps_by_recommendation,
        top_savings_opportunities=top_savings_opportunities,
        recent_decisions=recent_decisions,
    )
