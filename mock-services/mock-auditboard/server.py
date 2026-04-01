"""Mock AuditBoard Service -- Vendor Risk / Compliance Data

Serves vendor risk assessments and audit findings for TechDebt local development.
Data aligns with the 100 seeded applications in 005_seed_data.py.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Mock AuditBoard", version="1.0.0")

# ---------------------------------------------------------------------------
# Deterministic UUID helper
# ---------------------------------------------------------------------------
NS = uuid.UUID("c2d3e4f5-a6b7-8901-cdef-ab2345678901")


def _uid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# ---------------------------------------------------------------------------
# Seed data -- ~25 vendors matching apps with data_source="auditboard"
# plus other key vendors
# ---------------------------------------------------------------------------
VENDORS: list[dict] = [
    # Security vendors (primary auditboard source)
    {"id": _uid("v-crowdstrike"), "vendor_name": "CrowdStrike", "product": "CrowdStrike Falcon",
     "risk_score": 3, "compliance_status": "compliant", "last_audit_date": "2025-11-15",
     "findings_count": 0, "critical_findings": 0, "category": "Security",
     "audit_history": [
         {"date": "2025-11-15", "type": "annual", "result": "pass", "findings": 0},
         {"date": "2024-11-10", "type": "annual", "result": "pass", "findings": 1},
     ]},
    {"id": _uid("v-paloalto"), "vendor_name": "Palo Alto Networks", "product": "Palo Alto Prisma",
     "risk_score": 5, "compliance_status": "compliant", "last_audit_date": "2025-10-20",
     "findings_count": 1, "critical_findings": 0, "category": "Security",
     "audit_history": [
         {"date": "2025-10-20", "type": "annual", "result": "pass", "findings": 1},
         {"date": "2024-10-18", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-tenable"), "vendor_name": "Tenable", "product": "Tenable.io",
     "risk_score": 4, "compliance_status": "compliant", "last_audit_date": "2025-09-05",
     "findings_count": 0, "critical_findings": 0, "category": "Security",
     "audit_history": [
         {"date": "2025-09-05", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-qualys"), "vendor_name": "Qualys", "product": "Qualys VMDR",
     "risk_score": 35, "compliance_status": "pending_review", "last_audit_date": "2025-03-12",
     "findings_count": 4, "critical_findings": 1, "category": "Security",
     "audit_history": [
         {"date": "2025-03-12", "type": "annual", "result": "conditional_pass", "findings": 4},
         {"date": "2024-03-08", "type": "annual", "result": "pass", "findings": 1},
     ]},
    {"id": _uid("v-rapid7"), "vendor_name": "Rapid7", "product": "Rapid7 InsightVM",
     "risk_score": 38, "compliance_status": "pending_review", "last_audit_date": "2025-04-22",
     "findings_count": 5, "critical_findings": 1, "category": "Security",
     "audit_history": [
         {"date": "2025-04-22", "type": "annual", "result": "conditional_pass", "findings": 5},
     ]},
    {"id": _uid("v-wiz"), "vendor_name": "Wiz", "product": "Wiz",
     "risk_score": 4, "compliance_status": "compliant", "last_audit_date": "2025-12-01",
     "findings_count": 0, "critical_findings": 0, "category": "Security",
     "audit_history": [
         {"date": "2025-12-01", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-darktrace"), "vendor_name": "Darktrace", "product": "Darktrace",
     "risk_score": 42, "compliance_status": "non_compliant", "last_audit_date": "2025-01-18",
     "findings_count": 7, "critical_findings": 2, "category": "Security",
     "audit_history": [
         {"date": "2025-01-18", "type": "annual", "result": "fail", "findings": 7},
         {"date": "2024-01-15", "type": "annual", "result": "conditional_pass", "findings": 3},
     ]},
    {"id": _uid("v-carbonblack"), "vendor_name": "VMware", "product": "Carbon Black",
     "risk_score": 60, "compliance_status": "non_compliant", "last_audit_date": "2024-06-10",
     "findings_count": 9, "critical_findings": 3, "category": "Security",
     "audit_history": [
         {"date": "2024-06-10", "type": "annual", "result": "fail", "findings": 9},
         {"date": "2023-06-05", "type": "annual", "result": "conditional_pass", "findings": 4},
     ]},

    # Major vendors (cross-category)
    {"id": _uid("v-microsoft"), "vendor_name": "Microsoft", "product": "Microsoft 365 / Azure / Teams",
     "risk_score": 2, "compliance_status": "compliant", "last_audit_date": "2025-12-10",
     "findings_count": 0, "critical_findings": 0, "category": "Multi-Product",
     "audit_history": [
         {"date": "2025-12-10", "type": "annual", "result": "pass", "findings": 0},
         {"date": "2024-12-08", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-atlassian"), "vendor_name": "Atlassian", "product": "Jira / Confluence / Trello",
     "risk_score": 12, "compliance_status": "compliant", "last_audit_date": "2025-08-20",
     "findings_count": 2, "critical_findings": 0, "category": "Multi-Product",
     "audit_history": [
         {"date": "2025-08-20", "type": "annual", "result": "pass", "findings": 2},
         {"date": "2024-08-15", "type": "annual", "result": "pass", "findings": 1},
     ]},
    {"id": _uid("v-salesforce"), "vendor_name": "Salesforce", "product": "Slack / Tableau / Quip",
     "risk_score": 6, "compliance_status": "compliant", "last_audit_date": "2025-09-15",
     "findings_count": 1, "critical_findings": 0, "category": "Multi-Product",
     "audit_history": [
         {"date": "2025-09-15", "type": "annual", "result": "pass", "findings": 1},
     ]},
    {"id": _uid("v-google"), "vendor_name": "Google", "product": "Google Workspace / Looker",
     "risk_score": 5, "compliance_status": "compliant", "last_audit_date": "2025-10-01",
     "findings_count": 0, "critical_findings": 0, "category": "Multi-Product",
     "audit_history": [
         {"date": "2025-10-01", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-oracle"), "vendor_name": "Oracle", "product": "NetSuite",
     "risk_score": 8, "compliance_status": "compliant", "last_audit_date": "2025-07-22",
     "findings_count": 1, "critical_findings": 0, "category": "Finance",
     "audit_history": [
         {"date": "2025-07-22", "type": "annual", "result": "pass", "findings": 1},
     ]},
    {"id": _uid("v-workday"), "vendor_name": "Workday", "product": "Workday HCM",
     "risk_score": 2, "compliance_status": "compliant", "last_audit_date": "2025-11-01",
     "findings_count": 0, "critical_findings": 0, "category": "HR",
     "audit_history": [
         {"date": "2025-11-01", "type": "annual", "result": "pass", "findings": 0},
         {"date": "2024-11-05", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-amazon"), "vendor_name": "Amazon", "product": "AWS",
     "risk_score": 3, "compliance_status": "compliant", "last_audit_date": "2025-12-05",
     "findings_count": 0, "critical_findings": 0, "category": "Infrastructure",
     "audit_history": [
         {"date": "2025-12-05", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-snowflake"), "vendor_name": "Snowflake", "product": "Snowflake",
     "risk_score": 5, "compliance_status": "compliant", "last_audit_date": "2025-08-10",
     "findings_count": 0, "critical_findings": 0, "category": "Infrastructure",
     "audit_history": [
         {"date": "2025-08-10", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-datadog"), "vendor_name": "Datadog", "product": "Datadog",
     "risk_score": 5, "compliance_status": "compliant", "last_audit_date": "2025-10-15",
     "findings_count": 0, "critical_findings": 0, "category": "DevOps",
     "audit_history": [
         {"date": "2025-10-15", "type": "annual", "result": "pass", "findings": 0},
     ]},
    {"id": _uid("v-splunk"), "vendor_name": "Splunk", "product": "Splunk Enterprise",
     "risk_score": 8, "compliance_status": "compliant", "last_audit_date": "2025-06-20",
     "findings_count": 1, "critical_findings": 0, "category": "Security",
     "audit_history": [
         {"date": "2025-06-20", "type": "annual", "result": "pass", "findings": 1},
     ]},

    # Vendors with issues
    {"id": _uid("v-broadcom"), "vendor_name": "Broadcom", "product": "VMware vSphere",
     "risk_score": 55, "compliance_status": "non_compliant", "last_audit_date": "2025-02-15",
     "findings_count": 8, "critical_findings": 2, "category": "Infrastructure",
     "audit_history": [
         {"date": "2025-02-15", "type": "annual", "result": "fail", "findings": 8},
         {"date": "2024-02-10", "type": "annual", "result": "conditional_pass", "findings": 3},
     ]},
    {"id": _uid("v-domo"), "vendor_name": "Domo", "product": "Domo",
     "risk_score": 58, "compliance_status": "non_compliant", "last_audit_date": "2025-01-05",
     "findings_count": 6, "critical_findings": 2, "category": "Analytics",
     "audit_history": [
         {"date": "2025-01-05", "type": "annual", "result": "fail", "findings": 6},
     ]},
    {"id": _uid("v-planview"), "vendor_name": "Planview", "product": "Planview / Clarizen",
     "risk_score": 65, "compliance_status": "non_compliant", "last_audit_date": "2024-11-20",
     "findings_count": 10, "critical_findings": 3, "category": "Project Management",
     "audit_history": [
         {"date": "2024-11-20", "type": "annual", "result": "fail", "findings": 10},
     ]},
    {"id": _uid("v-cloudbees"), "vendor_name": "CloudBees", "product": "Jenkins (CloudBees)",
     "risk_score": 55, "compliance_status": "non_compliant", "last_audit_date": "2024-12-10",
     "findings_count": 7, "critical_findings": 2, "category": "DevOps",
     "audit_history": [
         {"date": "2024-12-10", "type": "annual", "result": "fail", "findings": 7},
     ]},
    {"id": _uid("v-akamai"), "vendor_name": "Akamai", "product": "Akamai",
     "risk_score": 50, "compliance_status": "pending_review", "last_audit_date": "2025-03-28",
     "findings_count": 5, "critical_findings": 1, "category": "Infrastructure",
     "audit_history": [
         {"date": "2025-03-28", "type": "annual", "result": "conditional_pass", "findings": 5},
     ]},
    {"id": _uid("v-freshworks"), "vendor_name": "Freshworks", "product": "Freshdesk",
     "risk_score": 40, "compliance_status": "pending_review", "last_audit_date": "2025-04-10",
     "findings_count": 3, "critical_findings": 0, "category": "Communication",
     "audit_history": [
         {"date": "2025-04-10", "type": "annual", "result": "conditional_pass", "findings": 3},
     ]},
]

# Build lookup by id
_vendors_by_id = {v["id"]: v for v in VENDORS}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-auditboard"}


@app.get("/api/v1/vendors")
async def list_vendors(
    compliance_status: Optional[str] = Query(None, description="Filter: compliant, non_compliant, pending_review"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_risk_score: Optional[int] = Query(None, ge=0, le=100),
    max_risk_score: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    results = VENDORS
    if compliance_status:
        results = [v for v in results if v["compliance_status"] == compliance_status]
    if category:
        results = [v for v in results if v["category"].lower() == category.lower()]
    if min_risk_score is not None:
        results = [v for v in results if v["risk_score"] >= min_risk_score]
    if max_risk_score is not None:
        results = [v for v in results if v["risk_score"] <= max_risk_score]

    total = len(results)
    # Return without audit_history in list view
    page = []
    for v in results[offset:offset + limit]:
        item = {k: v for k, v in v.items() if k != "audit_history"}
        page.append(item)

    return {"total": total, "offset": offset, "limit": limit, "vendors": page}


@app.get("/api/v1/vendors/{vendor_id}")
async def get_vendor(vendor_id: str):
    vendor = _vendors_by_id.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@app.get("/api/v1/risk-summary")
async def risk_summary():
    total = len(VENDORS)
    compliant = sum(1 for v in VENDORS if v["compliance_status"] == "compliant")
    non_compliant = sum(1 for v in VENDORS if v["compliance_status"] == "non_compliant")
    pending = sum(1 for v in VENDORS if v["compliance_status"] == "pending_review")

    avg_risk = round(sum(v["risk_score"] for v in VENDORS) / total, 1) if total else 0
    total_findings = sum(v["findings_count"] for v in VENDORS)
    total_critical = sum(v["critical_findings"] for v in VENDORS)

    high_risk = sorted(
        [v for v in VENDORS if v["risk_score"] >= 40],
        key=lambda x: x["risk_score"], reverse=True,
    )
    high_risk_summary = [
        {"vendor_name": v["vendor_name"], "product": v["product"],
         "risk_score": v["risk_score"], "compliance_status": v["compliance_status"],
         "critical_findings": v["critical_findings"]}
        for v in high_risk
    ]

    return {
        "total_vendors": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "pending_review": pending,
        "average_risk_score": avg_risk,
        "total_findings": total_findings,
        "total_critical_findings": total_critical,
        "high_risk_vendors": high_risk_summary,
    }
