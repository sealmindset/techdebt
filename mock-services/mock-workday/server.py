"""Mock Workday Service -- Procurement / Sourcing Data

Serves software contract and spend data for TechDebt local development.
Data aligns with the 100 seeded applications in 005_seed_data.py.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="Mock Workday", version="1.0.0")

# ---------------------------------------------------------------------------
# Deterministic UUID helper (matches seed data namespace)
# ---------------------------------------------------------------------------
NS = uuid.UUID("b1c2d3e4-f5a6-7890-bcde-fa1234567890")


def _uid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# ---------------------------------------------------------------------------
# Seed data -- ~30 contracts matching apps with data_source="workday"
# ---------------------------------------------------------------------------
# Fields: id, vendor, product_name, annual_cost, contract_start, contract_end,
#          payment_terms, department, status, category
CONTRACTS: list[dict] = [
    # Productivity
    {"id": _uid("c-ms365"), "vendor": "Microsoft", "product_name": "Microsoft 365",
     "annual_cost": 1800000, "contract_start": "2024-07-01", "contract_end": "2027-06-30",
     "payment_terms": "annual", "department": "All Departments", "status": "active", "category": "Productivity"},
    {"id": _uid("c-gworkspace"), "vendor": "Google", "product_name": "Google Workspace",
     "annual_cost": 420000, "contract_start": "2023-09-16", "contract_end": "2025-09-15",
     "payment_terms": "annual", "department": "Marketing", "status": "active", "category": "Productivity"},
    {"id": _uid("c-confluence"), "vendor": "Atlassian", "product_name": "Confluence",
     "annual_cost": 54000, "contract_start": "2023-05-01", "contract_end": "2025-04-30",
     "payment_terms": "annual", "department": "Engineering", "status": "expiring_soon", "category": "Productivity"},
    {"id": _uid("c-quip"), "vendor": "Salesforce", "product_name": "Quip",
     "annual_cost": 24000, "contract_start": "2022-07-01", "contract_end": "2024-06-30",
     "payment_terms": "annual", "department": "Sales", "status": "expired", "category": "Productivity"},

    # Security
    {"id": _uid("c-splunk"), "vendor": "Splunk", "product_name": "Splunk Enterprise",
     "annual_cost": 750000, "contract_start": "2024-08-16", "contract_end": "2026-08-15",
     "payment_terms": "annual", "department": "Security", "status": "active", "category": "Security"},

    # DevOps
    {"id": _uid("c-jira"), "vendor": "Atlassian", "product_name": "Jira Software",
     "annual_cost": 120000, "contract_start": "2024-11-01", "contract_end": "2026-10-31",
     "payment_terms": "annual", "department": "Engineering", "status": "active", "category": "DevOps"},
    {"id": _uid("c-datadog"), "vendor": "Datadog", "product_name": "Datadog",
     "annual_cost": 360000, "contract_start": "2025-05-01", "contract_end": "2027-04-30",
     "payment_terms": "annual", "department": "Engineering", "status": "active", "category": "DevOps"},
    {"id": _uid("c-pagerduty"), "vendor": "PagerDuty", "product_name": "PagerDuty",
     "annual_cost": 84000, "contract_start": "2024-05-16", "contract_end": "2026-05-15",
     "payment_terms": "annual", "department": "Engineering", "status": "active", "category": "DevOps"},
    {"id": _uid("c-newrelic"), "vendor": "New Relic", "product_name": "New Relic",
     "annual_cost": 240000, "contract_start": "2023-09-01", "contract_end": "2025-08-31",
     "payment_terms": "annual", "department": "Engineering", "status": "expiring_soon", "category": "DevOps"},
    {"id": _uid("c-bamboo"), "vendor": "Atlassian", "product_name": "Bamboo",
     "annual_cost": 36000, "contract_start": "2022-04-01", "contract_end": "2024-03-31",
     "payment_terms": "annual", "department": "Engineering", "status": "expired", "category": "DevOps"},

    # HR
    {"id": _uid("c-workday-hcm"), "vendor": "Workday", "product_name": "Workday HCM",
     "annual_cost": 2500000, "contract_start": "2025-01-01", "contract_end": "2027-12-31",
     "payment_terms": "annual", "department": "HR", "status": "active", "category": "HR"},
    {"id": _uid("c-bamboohr"), "vendor": "BambooHR", "product_name": "BambooHR",
     "annual_cost": 60000, "contract_start": "2023-10-01", "contract_end": "2025-09-30",
     "payment_terms": "annual", "department": "HR", "status": "expiring_soon", "category": "HR"},
    {"id": _uid("c-greenhouse"), "vendor": "Greenhouse", "product_name": "Greenhouse",
     "annual_cost": 96000, "contract_start": "2024-12-01", "contract_end": "2026-11-30",
     "payment_terms": "annual", "department": "HR", "status": "active", "category": "HR"},
    {"id": _uid("c-lever"), "vendor": "Lever", "product_name": "Lever",
     "annual_cost": 72000, "contract_start": "2023-07-16", "contract_end": "2025-07-15",
     "payment_terms": "annual", "department": "HR", "status": "expiring_soon", "category": "HR"},
    {"id": _uid("c-paycom"), "vendor": "Paycom", "product_name": "Paycom",
     "annual_cost": 200000, "contract_start": "2025-04-01", "contract_end": "2027-03-31",
     "payment_terms": "annual", "department": "HR", "status": "active", "category": "HR"},
    {"id": _uid("c-namely"), "vendor": "Namely", "product_name": "Namely",
     "annual_cost": 36000, "contract_start": "2022-09-01", "contract_end": "2024-08-31",
     "payment_terms": "annual", "department": "HR", "status": "expired", "category": "HR"},

    # Finance
    {"id": _uid("c-concur"), "vendor": "SAP", "product_name": "SAP Concur",
     "annual_cost": 600000, "contract_start": "2025-02-01", "contract_end": "2027-01-31",
     "payment_terms": "annual", "department": "Finance", "status": "active", "category": "Finance"},
    {"id": _uid("c-netsuite"), "vendor": "Oracle", "product_name": "NetSuite",
     "annual_cost": 480000, "contract_start": "2025-07-01", "contract_end": "2027-06-30",
     "payment_terms": "annual", "department": "Finance", "status": "active", "category": "Finance"},
    {"id": _uid("c-coupa"), "vendor": "Coupa", "product_name": "Coupa",
     "annual_cost": 360000, "contract_start": "2025-01-01", "contract_end": "2026-12-31",
     "payment_terms": "annual", "department": "Finance", "status": "active", "category": "Finance"},
    {"id": _uid("c-expensify"), "vendor": "Expensify", "product_name": "Expensify",
     "annual_cost": 72000, "contract_start": "2023-11-01", "contract_end": "2025-10-31",
     "payment_terms": "annual", "department": "Finance", "status": "expiring_soon", "category": "Finance"},
    {"id": _uid("c-tipalti"), "vendor": "Tipalti", "product_name": "Tipalti",
     "annual_cost": 96000, "contract_start": "2023-07-01", "contract_end": "2025-06-30",
     "payment_terms": "monthly", "department": "Finance", "status": "expiring_soon", "category": "Finance"},
    {"id": _uid("c-avalara"), "vendor": "Avalara", "product_name": "Avalara",
     "annual_cost": 42000, "contract_start": "2024-11-16", "contract_end": "2026-11-15",
     "payment_terms": "annual", "department": "Finance", "status": "active", "category": "Finance"},
    {"id": _uid("c-blackline"), "vendor": "BlackLine", "product_name": "BlackLine",
     "annual_cost": 144000, "contract_start": "2025-03-01", "contract_end": "2027-02-28",
     "payment_terms": "annual", "department": "Finance", "status": "active", "category": "Finance"},
    {"id": _uid("c-sage"), "vendor": "Sage", "product_name": "Sage Intacct",
     "annual_cost": 108000, "contract_start": "2022-06-01", "contract_end": "2024-05-31",
     "payment_terms": "annual", "department": "Finance", "status": "expired", "category": "Finance"},

    # Collaboration / Communication / PM / Infrastructure (workday source)
    {"id": _uid("c-webex"), "vendor": "Cisco", "product_name": "Webex",
     "annual_cost": 180000, "contract_start": "2022-05-01", "contract_end": "2024-04-30",
     "payment_terms": "annual", "department": "All Departments", "status": "expired", "category": "Collaboration"},
    {"id": _uid("c-bluejeans"), "vendor": "Verizon", "product_name": "BlueJeans",
     "annual_cost": 48000, "contract_start": "2022-03-01", "contract_end": "2024-02-28",
     "payment_terms": "annual", "department": "Operations", "status": "expired", "category": "Collaboration"},
    {"id": _uid("c-twilio"), "vendor": "Twilio", "product_name": "Twilio",
     "annual_cost": 144000, "contract_start": "2024-12-16", "contract_end": "2026-12-15",
     "payment_terms": "monthly", "department": "Engineering", "status": "active", "category": "Communication"},
    {"id": _uid("c-sendgrid"), "vendor": "Twilio", "product_name": "SendGrid",
     "annual_cost": 36000, "contract_start": "2024-10-01", "contract_end": "2026-09-30",
     "payment_terms": "annual", "department": "Marketing", "status": "active", "category": "Communication"},
    {"id": _uid("c-zendesk"), "vendor": "Zendesk", "product_name": "Zendesk",
     "annual_cost": 180000, "contract_start": "2025-03-01", "contract_end": "2027-02-28",
     "payment_terms": "annual", "department": "Operations", "status": "active", "category": "Communication"},
    {"id": _uid("c-smartsheet"), "vendor": "Smartsheet", "product_name": "Smartsheet",
     "annual_cost": 72000, "contract_start": "2023-09-16", "contract_end": "2025-09-15",
     "payment_terms": "annual", "department": "Operations", "status": "expiring_soon", "category": "Project Management"},
    {"id": _uid("c-aws"), "vendor": "Amazon", "product_name": "AWS",
     "annual_cost": 2400000, "contract_start": "2025-07-01", "contract_end": "2027-06-30",
     "payment_terms": "monthly", "department": "Engineering", "status": "active", "category": "Infrastructure"},
    {"id": _uid("c-azure"), "vendor": "Microsoft", "product_name": "Azure",
     "annual_cost": 1200000, "contract_start": "2025-07-01", "contract_end": "2027-06-30",
     "payment_terms": "monthly", "department": "Engineering", "status": "active", "category": "Infrastructure"},
]

# Build lookup by id
_contracts_by_id = {c["id"]: c for c in CONTRACTS}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-workday"}


@app.get("/api/v1/procurement/contracts")
async def list_contracts(
    vendor: Optional[str] = Query(None, description="Filter by vendor name"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by contract status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    results = CONTRACTS
    if vendor:
        results = [c for c in results if c["vendor"].lower() == vendor.lower()]
    if department:
        results = [c for c in results if c["department"].lower() == department.lower()]
    if status:
        results = [c for c in results if c["status"] == status]
    if category:
        results = [c for c in results if c["category"].lower() == category.lower()]

    total = len(results)
    page = results[offset:offset + limit]
    return {"total": total, "offset": offset, "limit": limit, "contracts": page}


@app.get("/api/v1/procurement/contracts/{contract_id}")
async def get_contract(contract_id: str):
    contract = _contracts_by_id.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@app.get("/api/v1/procurement/spend-summary")
async def spend_summary(
    group_by: str = Query("vendor", description="Group by: vendor, category, department"),
):
    aggregation: dict[str, dict] = {}
    for c in CONTRACTS:
        key = c.get(group_by, c["vendor"])
        if key not in aggregation:
            aggregation[key] = {"name": key, "total_annual_spend": 0, "contract_count": 0,
                                "active_contracts": 0, "expiring_soon": 0, "expired": 0}
        agg = aggregation[key]
        agg["total_annual_spend"] += c["annual_cost"]
        agg["contract_count"] += 1
        if c["status"] == "active":
            agg["active_contracts"] += 1
        elif c["status"] == "expiring_soon":
            agg["expiring_soon"] += 1
        elif c["status"] == "expired":
            agg["expired"] += 1

    summary = sorted(aggregation.values(), key=lambda x: x["total_annual_spend"], reverse=True)
    total_spend = sum(c["annual_cost"] for c in CONTRACTS)
    return {
        "total_annual_spend": total_spend,
        "group_by": group_by,
        "groups": summary,
    }
