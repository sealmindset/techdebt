"""Mock Entra ID Service -- Login / Usage Analytics

Serves sign-in and application usage data for TechDebt local development.
Data aligns with the 100 seeded applications in 005_seed_data.py.
"""

from __future__ import annotations

import hashlib
import random
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Mock Entra ID", version="1.0.0")

# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------
NS = uuid.UUID("d3e4f5a6-b7c8-9012-defa-bc3456789012")


def _uid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


def _deterministic_seed(label: str) -> int:
    """Return a stable integer seed for a given label."""
    return int(hashlib.md5(label.encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------------------
# Seed data -- ~40 apps with sign-in analytics
# Covers all apps with data_source="entra_id" plus major apps that would
# naturally appear in Entra ID sign-in logs
# ---------------------------------------------------------------------------

def _make_app(name: str, app_id: str, unique_30d: int, unique_90d: int,
              total_30d: int, last_sign_in: str, trend: str,
              category: str) -> dict:
    """Build an app entry with deterministic daily/monthly usage data."""
    rng = random.Random(_deterministic_seed(name))

    # Generate 30 days of daily active users (slight variation around mean)
    mean_daily = max(1, unique_30d // 22)  # ~22 working days
    daily_active = []
    for day in range(30):
        day_str = f"2026-03-{(day + 1):02d}" if day < 28 else f"2026-03-{(day + 1):02d}"
        # Weekend dip
        is_weekend = (day % 7) in (5, 6)
        factor = 0.15 if is_weekend else 1.0
        val = max(0, int(mean_daily * factor * rng.uniform(0.7, 1.3)))
        daily_active.append({"date": day_str, "users": val})

    # Generate 3 months of monthly active users
    monthly_active = [
        {"month": "2026-01", "users": int(unique_90d * rng.uniform(0.28, 0.36))},
        {"month": "2026-02", "users": int(unique_90d * rng.uniform(0.30, 0.38))},
        {"month": "2026-03", "users": unique_30d},
    ]

    sign_in_locations = _gen_locations(rng, total_30d)
    device_types = _gen_devices(rng, total_30d)

    return {
        "app_name": name,
        "app_id": app_id,
        "unique_users_30d": unique_30d,
        "unique_users_90d": unique_90d,
        "total_sign_ins_30d": total_30d,
        "last_sign_in": last_sign_in,
        "trend": trend,
        "category": category,
        "daily_active_users": daily_active,
        "monthly_active_users": monthly_active,
        "sign_in_locations": sign_in_locations,
        "device_types": device_types,
    }


def _gen_locations(rng: random.Random, total: int) -> list[dict]:
    locations = ["United States", "United Kingdom", "Germany", "India", "Canada"]
    weights = [0.65, 0.12, 0.08, 0.10, 0.05]
    result = []
    for loc, w in zip(locations, weights):
        count = max(1, int(total * w * rng.uniform(0.8, 1.2)))
        result.append({"location": loc, "sign_in_count": count})
    return result


def _gen_devices(rng: random.Random, total: int) -> list[dict]:
    devices = [
        {"device_type": "Windows", "percentage": round(rng.uniform(55, 70), 1)},
        {"device_type": "macOS", "percentage": round(rng.uniform(18, 30), 1)},
        {"device_type": "iOS", "percentage": round(rng.uniform(3, 8), 1)},
        {"device_type": "Android", "percentage": round(rng.uniform(2, 5), 1)},
    ]
    # Normalize to 100
    total_pct = sum(d["percentage"] for d in devices)
    for d in devices:
        d["percentage"] = round(d["percentage"] / total_pct * 100, 1)
    return devices


# ---------------------------------------------------------------------------
# Application data
# ---------------------------------------------------------------------------
APPS: list[dict] = [
    # Apps explicitly sourced from entra_id in seed data
    _make_app("GitHub Enterprise", _uid("a-github"), 980, 990, 28500,
              "2026-03-31", "stable", "DevOps"),
    _make_app("Slack", _uid("a-slack"), 3800, 3900, 115000,
              "2026-03-31", "stable", "Collaboration"),
    _make_app("Microsoft Teams", _uid("a-teams"), 4900, 4950, 180000,
              "2026-03-31", "stable", "Collaboration"),
    _make_app("Power BI Pro", _uid("a-powerbi"), 850, 920, 12000,
              "2026-03-31", "increasing", "Analytics"),
    _make_app("Zoom", _uid("a-zoom"), 2800, 2900, 42000,
              "2026-03-31", "stable", "Communication"),
    _make_app("Asana", _uid("a-asana"), 680, 720, 8500,
              "2026-03-31", "stable", "Project Management"),
    _make_app("Monday.com", _uid("a-monday"), 450, 480, 5600,
              "2026-03-31", "increasing", "Project Management"),
    _make_app("Trello", _uid("a-trello"), 120, 180, 1200,
              "2026-03-30", "decreasing", "Project Management"),

    # Major apps that would appear in Entra SSO regardless of primary data source
    _make_app("Microsoft 365", _uid("a-ms365"), 4800, 4900, 210000,
              "2026-03-31", "stable", "Productivity"),
    _make_app("Google Workspace", _uid("a-gworkspace"), 580, 950, 4200,
              "2026-03-28", "decreasing", "Productivity"),
    _make_app("Notion", _uid("a-notion"), 720, 750, 9800,
              "2026-03-31", "increasing", "Productivity"),
    _make_app("Confluence", _uid("a-confluence"), 145, 380, 1100,
              "2026-03-25", "decreasing", "Productivity"),
    _make_app("Evernote Business", _uid("a-evernote"), 8, 22, 45,
              "2026-02-10", "decreasing", "Productivity"),
    _make_app("CrowdStrike Falcon", _uid("a-crowdstrike"), 5000, 5000, 5200,
              "2026-03-31", "stable", "Security"),
    _make_app("Jira Software", _uid("a-jira"), 850, 900, 18000,
              "2026-03-31", "stable", "DevOps"),
    _make_app("Datadog", _uid("a-datadog"), 920, 940, 14500,
              "2026-03-31", "stable", "DevOps"),
    _make_app("CircleCI", _uid("a-circleci"), 185, 190, 4200,
              "2026-03-31", "stable", "DevOps"),
    _make_app("Workday HCM", _uid("a-workday"), 4950, 4980, 38000,
              "2026-03-31", "stable", "HR"),
    _make_app("SAP Concur", _uid("a-concur"), 1850, 1900, 8500,
              "2026-03-31", "stable", "Finance"),
    _make_app("NetSuite", _uid("a-netsuite"), 490, 495, 6800,
              "2026-03-31", "stable", "Finance"),
    _make_app("Coupa", _uid("a-coupa"), 480, 490, 5200,
              "2026-03-31", "stable", "Finance"),
    _make_app("Figma", _uid("a-figma"), 550, 570, 9200,
              "2026-03-31", "increasing", "Collaboration"),
    _make_app("Miro", _uid("a-miro"), 380, 420, 3800,
              "2026-03-31", "stable", "Collaboration"),
    _make_app("Tableau", _uid("a-tableau"), 420, 460, 4500,
              "2026-03-31", "stable", "Analytics"),
    _make_app("Snowflake", _uid("a-snowflake"), 280, 290, 8200,
              "2026-03-31", "stable", "Infrastructure"),
    _make_app("AWS", _uid("a-aws"), 950, 960, 42000,
              "2026-03-31", "stable", "Infrastructure"),
    _make_app("Zendesk", _uid("a-zendesk"), 460, 470, 9800,
              "2026-03-31", "stable", "Communication"),
    _make_app("Intercom", _uid("a-intercom"), 95, 98, 2800,
              "2026-03-31", "stable", "Communication"),
    _make_app("PagerDuty", _uid("a-pagerduty"), 195, 198, 4800,
              "2026-03-31", "stable", "DevOps"),
    _make_app("Amplitude", _uid("a-amplitude"), 190, 195, 3200,
              "2026-03-31", "stable", "Analytics"),

    # Low-adoption apps (showing declining usage)
    _make_app("Dropbox Paper", _uid("a-dropbox-paper"), 22, 65, 120,
              "2026-03-15", "decreasing", "Productivity"),
    _make_app("Quip", _uid("a-quip"), 15, 50, 80,
              "2026-02-20", "decreasing", "Productivity"),
    _make_app("Carbon Black", _uid("a-carbonblack"), 45, 120, 200,
              "2026-03-10", "decreasing", "Security"),
    _make_app("Bamboo", _uid("a-bamboo"), 18, 55, 90,
              "2026-02-05", "decreasing", "DevOps"),
    _make_app("Webex", _uid("a-webex"), 60, 180, 350,
              "2026-03-20", "decreasing", "Collaboration"),
    _make_app("BlueJeans", _uid("a-bluejeans"), 5, 15, 12,
              "2026-01-28", "decreasing", "Collaboration"),
    _make_app("Sisense", _uid("a-sisense"), 30, 85, 180,
              "2026-03-05", "decreasing", "Analytics"),
    _make_app("Domo", _uid("a-domo"), 55, 120, 350,
              "2026-03-18", "decreasing", "Analytics"),
    _make_app("Vonage", _uid("a-vonage"), 25, 70, 100,
              "2026-02-15", "decreasing", "Communication"),
    _make_app("Teamwork", _uid("a-teamwork"), 15, 45, 60,
              "2026-02-08", "decreasing", "Project Management"),
]

# Build lookups
_apps_by_id = {a["app_id"]: a for a in APPS}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-entra"}


@app.get("/api/v1/applications/sign-ins")
async def list_sign_ins(
    trend: Optional[str] = Query(None, description="Filter: increasing, decreasing, stable"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_users: Optional[int] = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    results = APPS
    if trend:
        results = [a for a in results if a["trend"] == trend]
    if category:
        results = [a for a in results if a["category"].lower() == category.lower()]
    if min_users is not None:
        results = [a for a in results if a["unique_users_30d"] >= min_users]

    total = len(results)
    # Return summary fields only (no daily/monthly breakdown)
    page = []
    for a in results[offset:offset + limit]:
        page.append({
            "app_name": a["app_name"],
            "app_id": a["app_id"],
            "unique_users_30d": a["unique_users_30d"],
            "unique_users_90d": a["unique_users_90d"],
            "total_sign_ins_30d": a["total_sign_ins_30d"],
            "last_sign_in": a["last_sign_in"],
            "trend": a["trend"],
            "category": a["category"],
        })

    return {"total": total, "offset": offset, "limit": limit, "applications": page}


@app.get("/api/v1/applications/{app_id}/usage")
async def get_app_usage(app_id: str):
    application = _apps_by_id.get(app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.get("/api/v1/applications/usage-summary")
async def usage_summary():
    total_apps = len(APPS)
    total_unique_30d = sum(a["unique_users_30d"] for a in APPS)
    total_sign_ins_30d = sum(a["total_sign_ins_30d"] for a in APPS)

    increasing = sum(1 for a in APPS if a["trend"] == "increasing")
    decreasing = sum(1 for a in APPS if a["trend"] == "decreasing")
    stable = sum(1 for a in APPS if a["trend"] == "stable")

    # Top 10 by unique users
    top_by_users = sorted(APPS, key=lambda x: x["unique_users_30d"], reverse=True)[:10]
    top_summary = [
        {"app_name": a["app_name"], "unique_users_30d": a["unique_users_30d"],
         "total_sign_ins_30d": a["total_sign_ins_30d"], "trend": a["trend"]}
        for a in top_by_users
    ]

    # Lowest adoption (bottom 10)
    bottom_by_users = sorted(APPS, key=lambda x: x["unique_users_30d"])[:10]
    bottom_summary = [
        {"app_name": a["app_name"], "unique_users_30d": a["unique_users_30d"],
         "total_sign_ins_30d": a["total_sign_ins_30d"], "trend": a["trend"]}
        for a in bottom_by_users
    ]

    # By category
    cat_agg: dict[str, dict] = {}
    for a in APPS:
        cat = a["category"]
        if cat not in cat_agg:
            cat_agg[cat] = {"category": cat, "app_count": 0, "total_users_30d": 0}
        cat_agg[cat]["app_count"] += 1
        cat_agg[cat]["total_users_30d"] += a["unique_users_30d"]

    by_category = sorted(cat_agg.values(), key=lambda x: x["total_users_30d"], reverse=True)

    return {
        "total_applications": total_apps,
        "total_unique_users_30d": total_unique_30d,
        "total_sign_ins_30d": total_sign_ins_30d,
        "trend_breakdown": {
            "increasing": increasing,
            "decreasing": decreasing,
            "stable": stable,
        },
        "top_apps_by_users": top_summary,
        "lowest_adoption_apps": bottom_summary,
        "by_category": by_category,
    }
