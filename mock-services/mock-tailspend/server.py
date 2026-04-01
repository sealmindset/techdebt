"""Mock Tailspend Service -- Vendor Spend Analytics

Serves vendor spend data, capability metadata, and contract intelligence
for TechDebt local development. Simulates the Tailspend Analyzer API
with realistic Sleep Number vendor data.

Data aligns with Tailspend-sourced applications in 006_tailspend_seed.py.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="Mock Tailspend", version="1.0.0")

# ---------------------------------------------------------------------------
# Deterministic UUID helper
# ---------------------------------------------------------------------------
NS = uuid.UUID("e4f5a6b7-c8d9-0123-efab-cd4567890123")


def _uid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


# ---------------------------------------------------------------------------
# Seed data -- ~25 vendor spend records
# ---------------------------------------------------------------------------
# Group A: Overlapping vendors (enrich existing TechDebt apps)
# Group B: New SaaS vendors (become new Application records)
# Group C: Tail-spend / rationalization candidates

VENDOR_SPEND: list[dict] = [
    # ======================================================================
    # GROUP A -- Overlapping vendors (exist in other data sources)
    # ======================================================================
    {
        "id": _uid("vs-microsoft"),
        "vendor_name": "Microsoft",
        "vendor_number": "VN-10001",
        "vendor_type": "SOFTWARE",
        "department": "All Departments",
        "annual_spend": {"2024": 3150000, "2025": 3240000, "2026": 1620000},
        "category": "Productivity",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,EMPLOYEE_DATA,PROPRIETARY_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2024-07-01",
            "end_date": "2027-06-30",
            "auto_renew": True,
            "risks": ["Large multi-product dependency", "Price escalation on renewal"],
            "services_products": "Microsoft 365, Azure, Power BI, Teams",
            "summary": "Enterprise agreement covering productivity suite, cloud infrastructure, and analytics.",
            "confidence": 0.95,
        },
    },
    {
        "id": _uid("vs-amazon"),
        "vendor_name": "Amazon",
        "vendor_number": "VN-10002",
        "vendor_type": "SOFTWARE",
        "department": "Engineering",
        "annual_spend": {"2024": 2280000, "2025": 2520000, "2026": 1380000},
        "category": "Infrastructure",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "PAAS,HOSTING",
        "commercial_model": "CONSUMPTION_BASED",
        "data_access_level": "PII,PCI,PROPRIETARY_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-07-01",
            "end_date": "2027-06-30",
            "auto_renew": False,
            "risks": ["Consumption growth exceeding budget", "Egress cost volatility"],
            "services_products": "AWS EC2, S3, RDS, Lambda, EKS",
            "summary": "Enterprise discount program for cloud compute, storage, and managed services.",
            "confidence": 0.93,
        },
    },
    {
        "id": _uid("vs-salesforce"),
        "vendor_name": "Salesforce",
        "vendor_number": "VN-10003",
        "vendor_type": "SOFTWARE",
        "department": "Sales",
        "annual_spend": {"2024": 648000, "2025": 672000, "2026": 336000},
        "category": "Sales",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-01-01",
            "end_date": "2027-12-31",
            "auto_renew": True,
            "risks": ["Auto-renewal with 60-day notice window", "Shelfware on unused licenses"],
            "services_products": "Sales Cloud, Service Cloud, Slack, Quip",
            "summary": "CRM platform with integrated communication tools for sales and service teams.",
            "confidence": 0.91,
        },
    },
    {
        "id": _uid("vs-atlassian"),
        "vendor_name": "Atlassian",
        "vendor_number": "VN-10004",
        "vendor_type": "SOFTWARE",
        "department": "Engineering",
        "annual_spend": {"2024": 210000, "2025": 222000, "2026": 111000},
        "category": "DevOps",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2024-11-01",
            "end_date": "2026-10-31",
            "auto_renew": True,
            "risks": ["Cloud migration price increase", "Bundled products inflate cost"],
            "services_products": "Jira Software, Confluence, Trello, Bitbucket",
            "summary": "Development and project management suite for engineering teams.",
            "confidence": 0.90,
        },
    },
    {
        "id": _uid("vs-sap"),
        "vendor_name": "SAP",
        "vendor_number": "VN-10005",
        "vendor_type": "SOFTWARE",
        "department": "Finance",
        "annual_spend": {"2024": 588000, "2025": 612000, "2026": 306000},
        "category": "Finance",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PCI,EMPLOYEE_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-02-01",
            "end_date": "2027-01-31",
            "auto_renew": True,
            "risks": ["Indirect access licensing complexity", "Integration maintenance burden"],
            "services_products": "SAP Concur, SAP Analytics Cloud",
            "summary": "Expense management and analytics platform for finance operations.",
            "confidence": 0.92,
        },
    },
    {
        "id": _uid("vs-oracle"),
        "vendor_name": "Oracle",
        "vendor_number": "VN-10006",
        "vendor_type": "SOFTWARE",
        "department": "Finance",
        "annual_spend": {"2024": 468000, "2025": 492000, "2026": 246000},
        "category": "Finance",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PCI,PROPRIETARY_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-07-01",
            "end_date": "2027-06-30",
            "auto_renew": True,
            "risks": ["Auto-renewal with 90-day notice", "Audit risk on license compliance"],
            "services_products": "NetSuite ERP, NetSuite CRM",
            "summary": "Core ERP system for financial management, GL, AP, and AR.",
            "confidence": 0.94,
        },
    },
    {
        "id": _uid("vs-datadog"),
        "vendor_name": "Datadog",
        "vendor_number": "VN-10007",
        "vendor_type": "SOFTWARE",
        "department": "Engineering",
        "annual_spend": {"2024": 336000, "2025": 384000, "2026": 210000},
        "category": "DevOps",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "OBSERVABILITY",
        "commercial_model": "CONSUMPTION_BASED",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2025-05-01",
            "end_date": "2027-04-30",
            "auto_renew": False,
            "risks": ["Consumption-based billing can spike", "Host count growth tied to cloud expansion"],
            "services_products": "Datadog APM, Log Management, Infrastructure Monitoring",
            "summary": "Unified observability platform for engineering operations.",
            "confidence": 0.91,
        },
    },
    {
        "id": _uid("vs-snowflake"),
        "vendor_name": "Snowflake",
        "vendor_number": "VN-10008",
        "vendor_type": "SOFTWARE",
        "department": "Engineering",
        "annual_spend": {"2024": 444000, "2025": 504000, "2026": 276000},
        "category": "Infrastructure",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "ANALYTICS",
        "commercial_model": "CONSUMPTION_BASED",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2024-12-01",
            "end_date": "2026-11-30",
            "auto_renew": False,
            "risks": ["Credit consumption exceeding committed spend", "Data gravity lock-in"],
            "services_products": "Snowflake Data Cloud, Snowpark, Cortex AI",
            "summary": "Cloud data warehouse for analytics, data engineering, and AI/ML workloads.",
            "confidence": 0.90,
        },
    },

    # ======================================================================
    # GROUP B -- New SaaS vendors (new Application records in TechDebt)
    # ======================================================================
    {
        "id": _uid("vs-docusign"),
        "vendor_name": "DocuSign",
        "vendor_number": "VN-20001",
        "vendor_type": "SOFTWARE",
        "department": "Legal",
        "annual_spend": {"2024": 78000, "2025": 84000, "2026": 42000},
        "category": "Productivity",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2025-01-15",
            "end_date": "2027-01-15",
            "auto_renew": True,
            "risks": ["Auto-renewal with 30-day notice"],
            "services_products": "DocuSign eSignature, CLM",
            "summary": "Electronic signature and contract lifecycle management for legal and procurement.",
            "confidence": 0.92,
        },
    },
    {
        "id": _uid("vs-okta"),
        "vendor_name": "Okta",
        "vendor_number": "VN-20002",
        "vendor_type": "SOFTWARE",
        "department": "Security",
        "annual_spend": {"2024": 180000, "2025": 192000, "2026": 96000},
        "category": "Security",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "CYBERSECURITY",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,EMPLOYEE_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-04-01",
            "end_date": "2027-03-31",
            "auto_renew": False,
            "risks": ["Single point of failure for authentication"],
            "services_products": "Okta SSO, Okta MFA, Okta Lifecycle Management",
            "summary": "Identity and access management platform for workforce and customer identity.",
            "confidence": 0.95,
        },
    },
    {
        "id": _uid("vs-servicenow"),
        "vendor_name": "ServiceNow",
        "vendor_number": "VN-20003",
        "vendor_type": "SOFTWARE",
        "department": "IT",
        "annual_spend": {"2024": 396000, "2025": 420000, "2026": 210000},
        "category": "IT Operations",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "EMPLOYEE_DATA,PROPRIETARY_DATA",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-01-01",
            "end_date": "2026-12-31",
            "auto_renew": True,
            "risks": ["Platform sprawl beyond ITSM", "Customization technical debt"],
            "services_products": "ServiceNow ITSM, ITOM, CMDB",
            "summary": "IT service management platform for incident, change, and asset management.",
            "confidence": 0.93,
        },
    },
    {
        "id": _uid("vs-adobe"),
        "vendor_name": "Adobe",
        "vendor_number": "VN-20004",
        "vendor_type": "SOFTWARE",
        "department": "Marketing",
        "annual_spend": {"2024": 144000, "2025": 156000, "2026": 78000},
        "category": "Marketing",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2024-10-01",
            "end_date": "2026-09-30",
            "auto_renew": True,
            "risks": ["License true-up on named users"],
            "services_products": "Adobe Creative Cloud, Adobe Acrobat",
            "summary": "Creative design and document management tools for marketing and brand teams.",
            "confidence": 0.90,
        },
    },
    {
        "id": _uid("vs-hubspot"),
        "vendor_name": "HubSpot",
        "vendor_number": "VN-20005",
        "vendor_type": "SOFTWARE",
        "department": "Marketing",
        "annual_spend": {"2024": 96000, "2025": 108000, "2026": 54000},
        "category": "Marketing",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2024-12-01",
            "end_date": "2026-11-30",
            "auto_renew": True,
            "risks": ["Overlap with Salesforce Marketing Cloud"],
            "services_products": "HubSpot Marketing Hub, CMS Hub",
            "summary": "Inbound marketing automation and content management for demand generation.",
            "confidence": 0.88,
        },
    },
    {
        "id": _uid("vs-gong"),
        "vendor_name": "Gong",
        "vendor_number": "VN-20006",
        "vendor_type": "SOFTWARE",
        "department": "Sales",
        "annual_spend": {"2024": 120000, "2025": 132000, "2026": 66000},
        "category": "Sales",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "ANALYTICS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2024-08-15",
            "end_date": "2026-08-15",
            "auto_renew": True,
            "risks": ["Call recording compliance requirements", "Data retention obligations"],
            "services_products": "Gong Revenue Intelligence, Gong Engage",
            "summary": "Revenue intelligence platform for sales call analytics and deal forecasting.",
            "confidence": 0.89,
        },
    },
    {
        "id": _uid("vs-shopify"),
        "vendor_name": "Shopify",
        "vendor_number": "VN-20007",
        "vendor_type": "SOFTWARE",
        "department": "E-Commerce",
        "annual_spend": {"2024": 216000, "2025": 240000, "2026": 120000},
        "category": "E-Commerce",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PCI",
        "criticality_level": "CRITICAL",
        "contract": {
            "start_date": "2025-07-01",
            "end_date": "2027-06-30",
            "auto_renew": False,
            "risks": ["Transaction fee escalation at scale", "Platform migration complexity"],
            "services_products": "Shopify Plus, Shopify POS",
            "summary": "E-commerce platform for Sleep Number direct-to-consumer online and retail sales.",
            "confidence": 0.91,
        },
    },
    {
        "id": _uid("vs-samsara"),
        "vendor_name": "Samsara",
        "vendor_number": "VN-20008",
        "vendor_type": "SOFTWARE",
        "department": "Operations",
        "annual_spend": {"2024": 84000, "2025": 96000, "2026": 48000},
        "category": "Operations",
        "product_or_service_category": "IOT_SERVICES",
        "service_subcategory": "OBSERVABILITY",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "IOT,EMPLOYEE_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2024-10-15",
            "end_date": "2026-10-15",
            "auto_renew": True,
            "risks": ["Hardware lock-in with proprietary sensors"],
            "services_products": "Samsara Fleet Management, Samsara Asset Tracking",
            "summary": "IoT fleet management for mattress delivery logistics and warehouse operations.",
            "confidence": 0.87,
        },
    },
    {
        "id": _uid("vs-thoughtspot"),
        "vendor_name": "ThoughtSpot",
        "vendor_number": "VN-20009",
        "vendor_type": "SOFTWARE",
        "department": "Engineering",
        "annual_spend": {"2024": 72000, "2025": 72000, "2026": 36000},
        "category": "Analytics",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "ANALYTICS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2024-12-01",
            "end_date": "2025-11-30",
            "auto_renew": True,
            "risks": ["Low adoption may not justify renewal", "Overlap with Tableau/Power BI"],
            "services_products": "ThoughtSpot Search & AI Analytics",
            "summary": "Search-driven analytics platform. Adoption has been below expectations.",
            "confidence": 0.82,
        },
    },
    {
        "id": _uid("vs-anaplan"),
        "vendor_name": "Anaplan",
        "vendor_number": "VN-20010",
        "vendor_type": "SOFTWARE",
        "department": "Finance",
        "annual_spend": {"2024": 168000, "2025": 180000, "2026": 90000},
        "category": "Finance",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "ANALYTICS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA,EMPLOYEE_DATA",
        "criticality_level": "IMPORTANT",
        "contract": {
            "start_date": "2025-03-01",
            "end_date": "2027-02-28",
            "auto_renew": False,
            "risks": ["Model complexity creates key-person dependency"],
            "services_products": "Anaplan Connected Planning, FP&A Module",
            "summary": "Financial planning and analysis platform for budgeting, forecasting, and scenario modeling.",
            "confidence": 0.91,
        },
    },

    # ======================================================================
    # GROUP C -- Tail-spend / rationalization candidates
    # ======================================================================
    {
        "id": _uid("vs-calendly"),
        "vendor_name": "Calendly",
        "vendor_number": "VN-30001",
        "vendor_type": "SOFTWARE",
        "department": "Sales",
        "annual_spend": {"2024": 11400, "2025": 12000, "2026": 6000},
        "category": "Productivity",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "auto_renew": True,
            "risks": ["Redundant with Microsoft Bookings in M365"],
            "services_products": "Calendly Professional",
            "summary": "Scheduling tool for sales team meeting booking. Overlaps with Teams/Bookings.",
            "confidence": 0.85,
        },
    },
    {
        "id": _uid("vs-grammarly"),
        "vendor_name": "Grammarly",
        "vendor_number": "VN-30002",
        "vendor_type": "SOFTWARE",
        "department": "Marketing",
        "annual_spend": {"2024": 16800, "2025": 18000, "2026": 9000},
        "category": "Productivity",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2025-01-15",
            "end_date": "2025-10-15",
            "auto_renew": True,
            "risks": ["Low adoption rate", "M365 Copilot provides similar capabilities"],
            "services_products": "Grammarly Business",
            "summary": "Writing assistant. Adoption is 24% with M365 Editor as free alternative.",
            "confidence": 0.80,
        },
    },
    {
        "id": _uid("vs-canva"),
        "vendor_name": "Canva",
        "vendor_number": "VN-30003",
        "vendor_type": "SOFTWARE",
        "department": "Marketing",
        "annual_spend": {"2024": 22200, "2025": 24000, "2026": 12000},
        "category": "Marketing",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2024-10-01",
            "end_date": "2025-09-30",
            "auto_renew": True,
            "risks": ["Functional overlap with Adobe Creative Cloud"],
            "services_products": "Canva Enterprise",
            "summary": "Design tool for non-designers. Overlaps significantly with Adobe CC licenses.",
            "confidence": 0.83,
        },
    },
    {
        "id": _uid("vs-surveymonkey"),
        "vendor_name": "SurveyMonkey",
        "vendor_number": "VN-30004",
        "vendor_type": "SOFTWARE",
        "department": "Marketing",
        "annual_spend": {"2024": 9000, "2025": 9600, "2026": 4800},
        "category": "Analytics",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2024-09-01",
            "end_date": "2025-08-31",
            "auto_renew": True,
            "risks": ["Low usage does not justify cost"],
            "services_products": "SurveyMonkey Enterprise",
            "summary": "Survey tool with 36% adoption. Microsoft Forms available at no additional cost.",
            "confidence": 0.78,
        },
    },
    {
        "id": _uid("vs-otterai"),
        "vendor_name": "Otter.ai",
        "vendor_number": "VN-30005",
        "vendor_type": "SOFTWARE",
        "department": "All Departments",
        "annual_spend": {"2024": 6000, "2025": 7200, "2026": 3600},
        "category": "Productivity",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2025-07-01",
            "end_date": "2026-06-30",
            "auto_renew": False,
            "risks": ["Meeting transcription data sensitivity"],
            "services_products": "Otter.ai Business",
            "summary": "AI meeting transcription. Growing adoption but Zoom AI Companion provides overlap.",
            "confidence": 0.84,
        },
    },
    {
        "id": _uid("vs-box"),
        "vendor_name": "Box",
        "vendor_number": "VN-30006",
        "vendor_type": "SOFTWARE",
        "department": "Engineering",
        "annual_spend": {"2024": 46800, "2025": 48000, "2026": 24000},
        "category": "Collaboration",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PII,PROPRIETARY_DATA",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2024-08-01",
            "end_date": "2025-07-31",
            "auto_renew": True,
            "risks": ["24% adoption with SharePoint/OneDrive as standard", "Data migration needed before cut"],
            "services_products": "Box Enterprise",
            "summary": "Cloud file storage. 24% adoption with OneDrive/SharePoint as enterprise standard.",
            "confidence": 0.86,
        },
    },
    {
        "id": _uid("vs-vimeo"),
        "vendor_name": "Vimeo",
        "vendor_number": "VN-30007",
        "vendor_type": "SOFTWARE",
        "department": "Marketing",
        "annual_spend": {"2024": 14400, "2025": 15000, "2026": 7500},
        "category": "Communication",
        "product_or_service_category": "SOFTWARE",
        "service_subcategory": "SAAS",
        "commercial_model": "SUBSCRIPTION",
        "data_access_level": "PROPRIETARY_DATA",
        "criticality_level": "NON_CRITICAL",
        "contract": {
            "start_date": "2024-07-01",
            "end_date": "2025-06-30",
            "auto_renew": True,
            "risks": ["30% adoption", "Zoom and Loom provide overlapping video capabilities"],
            "services_products": "Vimeo Enterprise",
            "summary": "Video hosting for marketing content. Low adoption with Loom/Zoom alternatives.",
            "confidence": 0.79,
        },
    },
]

# Build lookup by id
_vendors_by_id = {v["id"]: v for v in VENDOR_SPEND}


# ---------------------------------------------------------------------------
# Helper: strip contract details for list view
# ---------------------------------------------------------------------------
def _list_view(vendor: dict) -> dict:
    """Return vendor record without nested contract details."""
    result = {k: v for k, v in vendor.items() if k != "contract"}
    return result


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-tailspend"}


@app.get("/api/v1/vendor-spend/summary")
async def spend_summary():
    """High-level spend analytics across all vendors."""
    # Total spend (use 2025 as the reference year)
    total_spend = sum(v["annual_spend"].get("2025", 0) for v in VENDOR_SPEND)
    vendor_count = len(VENDOR_SPEND)

    # By category
    cat_totals: dict[str, float] = {}
    for v in VENDOR_SPEND:
        cat = v["category"]
        cat_totals[cat] = cat_totals.get(cat, 0) + v["annual_spend"].get("2025", 0)
    top_categories = sorted(
        [{"category": k, "total_spend": v} for k, v in cat_totals.items()],
        key=lambda x: x["total_spend"],
        reverse=True,
    )

    # Top vendors
    top_vendors = sorted(
        [{"vendor_name": v["vendor_name"], "total_spend": v["annual_spend"].get("2025", 0)}
         for v in VENDOR_SPEND],
        key=lambda x: x["total_spend"],
        reverse=True,
    )[:10]

    # By department
    dept_totals: dict[str, float] = {}
    for v in VENDOR_SPEND:
        dept = v["department"]
        dept_totals[dept] = dept_totals.get(dept, 0) + v["annual_spend"].get("2025", 0)
    spend_by_department = sorted(
        [{"department": k, "total_spend": v} for k, v in dept_totals.items()],
        key=lambda x: x["total_spend"],
        reverse=True,
    )

    # Criticality breakdown
    crit: dict[str, int] = {"CRITICAL": 0, "IMPORTANT": 0, "NON_CRITICAL": 0}
    for v in VENDOR_SPEND:
        level = v["criticality_level"]
        if level in crit:
            crit[level] += 1

    # Contract risk summary
    expiring_90d = 0
    auto_renew_count = 0
    high_risk_count = 0
    for v in VENDOR_SPEND:
        contract = v.get("contract")
        if not contract:
            continue
        if contract.get("end_date", "") <= "2025-06-30":
            expiring_90d += 1
        if contract.get("auto_renew"):
            auto_renew_count += 1
        if len(contract.get("risks", [])) >= 2:
            high_risk_count += 1

    return {
        "total_annual_spend": total_spend,
        "vendor_count": vendor_count,
        "top_categories": top_categories,
        "top_vendors": top_vendors,
        "spend_by_department": spend_by_department,
        "criticality_breakdown": crit,
        "contract_risk_summary": {
            "expiring_within_90_days": expiring_90d,
            "auto_renew_enabled": auto_renew_count,
            "high_risk_contracts": high_risk_count,
        },
    }


@app.get("/api/v1/vendor-spend/{vendor_id}")
async def get_vendor_spend(vendor_id: str):
    """Full vendor detail including contract and capabilities."""
    vendor = _vendors_by_id.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@app.get("/api/v1/vendor-spend")
async def list_vendor_spend(
    year: Optional[str] = Query(None, description="Filter spend year (e.g., 2025)"),
    vendor: Optional[str] = Query(None, description="Filter by vendor name"),
    department: Optional[str] = Query(None, description="Filter by department"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_spend: Optional[float] = Query(None, description="Minimum annual spend"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Paginated vendor spend list (contract details excluded)."""
    results = VENDOR_SPEND

    if vendor:
        results = [v for v in results if v["vendor_name"].lower() == vendor.lower()]
    if department:
        results = [v for v in results if v["department"].lower() == department.lower()]
    if category:
        results = [v for v in results if v["category"].lower() == category.lower()]
    if min_spend is not None:
        ref_year = year or "2025"
        results = [v for v in results if v["annual_spend"].get(ref_year, 0) >= min_spend]
    if year:
        results = [v for v in results if year in v["annual_spend"]]

    total = len(results)
    page = [_list_view(v) for v in results[offset:offset + limit]]
    return {"total": total, "offset": offset, "limit": limit, "vendors": page}
