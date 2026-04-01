"""Mock Microsoft Graph API Service

Mimics key Microsoft Graph API v1.0 endpoints that are critical for
SaaS rationalization and application intelligence:

- /v1.0/servicePrincipals       -- Enterprise app inventory (shadow IT discovery)
- /v1.0/auditLogs/signIns       -- Sign-in activity per application
- /v1.0/reports/m365Usage        -- Microsoft 365 suite usage reports
- /v1.0/subscribedSkus          -- License inventory & utilization
- /v1.0/applications             -- App registrations in the tenant

All data is deterministic and aligns with the 100 seeded applications
in TechDebt's 005_seed_data.py, plus 15 "shadow IT" apps not yet in
the TechDebt inventory (to demonstrate discovery capability).
"""

from __future__ import annotations

import hashlib
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Query

app = FastAPI(title="Mock Microsoft Graph API", version="1.0.0")

# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------
NS = uuid.UUID("e4f5a6b7-c8d9-0123-efab-cd4567890123")


def _uid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


def _seed(label: str) -> int:
    return int(hashlib.md5(label.encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------------------
# Service Principals -- Every SaaS app that authenticates through Entra ID
# shows up here. This is the DISCOVERY engine.
#
# Includes all 100 seeded TechDebt apps PLUS 15 shadow IT apps that only
# Graph knows about (not yet in the TechDebt applications table).
# ---------------------------------------------------------------------------

def _sp(name: str, vendor: str, category: str, enabled: bool = True,
        sso_mode: str = "oidc", sign_in_audience: str = "AzureADMyOrg",
        tags: list[str] | None = None, notes: str = "") -> dict:
    app_id = _uid(f"sp-{name.lower()}")
    rng = random.Random(_seed(name))
    created = datetime(2023, 1, 1) + timedelta(days=rng.randint(0, 730))
    return {
        "id": _uid(f"spobj-{name.lower()}"),
        "appId": app_id,
        "appDisplayName": name,
        "accountEnabled": enabled,
        "servicePrincipalType": "Application",
        "displayName": name,
        "homepage": f"https://{name.lower().replace(' ', '')}.com",
        "signInAudience": sign_in_audience,
        "preferredSingleSignOnMode": sso_mode,
        "tags": tags or [],
        "notes": notes,
        "publisherName": vendor,
        "appOwnerOrganizationId": _uid("tenant-org"),
        "createdDateTime": created.isoformat() + "Z",
        "category": category,  # custom field for our mock
    }


# All 100 known TechDebt apps as service principals
KNOWN_APPS = [
    _sp("Microsoft 365", "Microsoft", "Productivity"),
    _sp("Google Workspace", "Google", "Productivity"),
    _sp("Notion", "Notion Labs", "Productivity"),
    _sp("Confluence", "Atlassian", "Productivity"),
    _sp("Evernote Business", "Evernote", "Productivity", enabled=False),
    _sp("Coda", "Coda", "Productivity"),
    _sp("Quip", "Salesforce", "Productivity", enabled=False),
    _sp("Dropbox Paper", "Dropbox", "Productivity"),
    _sp("Zoho Workplace", "Zoho", "Productivity"),
    _sp("CrowdStrike Falcon", "CrowdStrike", "Security"),
    _sp("Palo Alto Prisma", "Palo Alto Networks", "Security"),
    _sp("Splunk Enterprise", "Splunk", "Security"),
    _sp("Tenable.io", "Tenable", "Security"),
    _sp("Qualys VMDR", "Qualys", "Security"),
    _sp("Rapid7 InsightVM", "Rapid7", "Security"),
    _sp("Snyk", "Snyk", "Security"),
    _sp("Wiz", "Wiz", "Security"),
    _sp("Darktrace", "Darktrace", "Security"),
    _sp("Carbon Black", "VMware", "Security", enabled=False),
    _sp("GitHub Enterprise", "GitHub", "DevOps"),
    _sp("Jira Software", "Atlassian", "DevOps"),
    _sp("GitLab Ultimate", "GitLab", "DevOps"),
    _sp("Jenkins (CloudBees)", "CloudBees", "DevOps"),
    _sp("CircleCI", "CircleCI", "DevOps"),
    _sp("Datadog", "Datadog", "DevOps"),
    _sp("PagerDuty", "PagerDuty", "DevOps"),
    _sp("Terraform Cloud", "HashiCorp", "DevOps"),
    _sp("New Relic", "New Relic", "DevOps"),
    _sp("Bamboo", "Atlassian", "DevOps", enabled=False),
    _sp("Workday HCM", "Workday", "HR"),
    _sp("BambooHR", "BambooHR", "HR"),
    _sp("ADP Workforce Now", "ADP", "HR"),
    _sp("Greenhouse", "Greenhouse", "HR"),
    _sp("Lever", "Lever", "HR"),
    _sp("Culture Amp", "Culture Amp", "HR"),
    _sp("15Five", "15Five", "HR"),
    _sp("Lattice", "Lattice", "HR"),
    _sp("SAP Concur", "SAP", "Finance"),
    _sp("NetSuite", "Oracle", "Finance"),
    _sp("Coupa", "Coupa", "Finance"),
    _sp("Expensify", "Expensify", "Finance"),
    _sp("Bill.com", "Bill.com", "Finance"),
    _sp("Brex", "Brex", "Finance"),
    _sp("Tipalti", "Tipalti", "Finance"),
    _sp("Avalara", "Avalara", "Finance"),
    _sp("BlackLine", "BlackLine", "Finance"),
    _sp("Slack", "Salesforce", "Collaboration"),
    _sp("Microsoft Teams", "Microsoft", "Collaboration"),
    _sp("Miro", "Miro", "Collaboration"),
    _sp("Figma", "Figma", "Collaboration"),
    _sp("Lucidchart", "Lucid Software", "Collaboration"),
    _sp("Mural", "Mural", "Collaboration"),
    _sp("Loom", "Loom", "Collaboration"),
    _sp("Webex", "Cisco", "Collaboration", enabled=False),
    _sp("Tableau", "Salesforce", "Analytics"),
    _sp("Power BI Pro", "Microsoft", "Analytics"),
    _sp("Looker", "Google", "Analytics"),
    _sp("Domo", "Domo", "Analytics"),
    _sp("Sisense", "Sisense", "Analytics", enabled=False),
    _sp("Mode Analytics", "ThoughtSpot", "Analytics"),
    _sp("Amplitude", "Amplitude", "Analytics"),
    _sp("Mixpanel", "Mixpanel", "Analytics"),
    _sp("Heap", "Contentsquare", "Analytics"),
    _sp("Zoom", "Zoom", "Communication"),
    _sp("Twilio", "Twilio", "Communication"),
    _sp("SendGrid", "Twilio", "Communication"),
    _sp("Mailchimp", "Intuit", "Communication"),
    _sp("Intercom", "Intercom", "Communication"),
    _sp("Zendesk", "Zendesk", "Communication"),
    _sp("Freshdesk", "Freshworks", "Communication"),
    _sp("Front", "Front", "Communication"),
    _sp("RingCentral", "RingCentral", "Communication"),
    _sp("Asana", "Asana", "Project Management"),
    _sp("Monday.com", "monday.com", "Project Management"),
    _sp("Smartsheet", "Smartsheet", "Project Management"),
    _sp("Wrike", "Citrix", "Project Management"),
    _sp("ClickUp", "ClickUp", "Project Management"),
    _sp("Trello", "Atlassian", "Project Management"),
    _sp("Airtable", "Airtable", "Project Management"),
    _sp("Planview", "Planview", "Project Management"),
    _sp("AWS", "Amazon", "Infrastructure"),
    _sp("Azure", "Microsoft", "Infrastructure"),
    _sp("Cloudflare", "Cloudflare", "Infrastructure"),
    _sp("Akamai", "Akamai", "Infrastructure"),
    _sp("Fastly", "Fastly", "Infrastructure"),
    _sp("Snowflake", "Snowflake", "Infrastructure"),
    _sp("MongoDB Atlas", "MongoDB", "Infrastructure"),
    _sp("Redis Cloud", "Redis", "Infrastructure"),
    _sp("Elastic Cloud", "Elastic", "Infrastructure"),
]

# 15 Shadow IT apps -- discovered by Graph but NOT in TechDebt inventory
SHADOW_APPS = [
    _sp("Grammarly Business", "Grammarly", "Productivity",
        tags=["shadow-it"], notes="Not in approved software catalog"),
    _sp("Calendly", "Calendly", "Productivity",
        tags=["shadow-it"], notes="Free tier being used by 45 users"),
    _sp("Canva Enterprise", "Canva", "Collaboration",
        tags=["shadow-it"], notes="Marketing team self-provisioned"),
    _sp("ChatGPT Enterprise", "OpenAI", "AI & ML",
        tags=["shadow-it"], notes="Multiple teams using without IT approval"),
    _sp("Notion AI", "Notion Labs", "AI & ML",
        tags=["shadow-it"], notes="Add-on to existing Notion licenses"),
    _sp("Vercel", "Vercel", "DevOps",
        tags=["shadow-it"], notes="Frontend team deployed preview environments"),
    _sp("Linear", "Linear", "Project Management",
        tags=["shadow-it"], notes="Engineering sub-team using instead of Jira"),
    _sp("Retool", "Retool", "DevOps",
        tags=["shadow-it"], notes="Internal tools built without IT oversight"),
    _sp("Postman", "Postman", "DevOps",
        tags=["shadow-it"], notes="API development tool, team plan"),
    _sp("Deel", "Deel", "HR",
        tags=["shadow-it"], notes="Contractor payments outside Workday"),
    _sp("Typeform", "Typeform", "Communication",
        tags=["shadow-it"], notes="Marketing surveys, not in approved list"),
    _sp("Zapier", "Zapier", "Automation",
        tags=["shadow-it"], notes="30+ active integrations across departments"),
    _sp("DocuSign", "DocuSign", "Finance",
        tags=["shadow-it", "high-priority"],
        notes="Contract signing -- potential compliance risk without IT governance"),
    _sp("Perplexity Pro", "Perplexity AI", "AI & ML",
        tags=["shadow-it"], notes="Research team expensing individual licenses"),
    _sp("Weights & Biases", "Weights & Biases", "AI & ML",
        tags=["shadow-it"], notes="ML team experiment tracking"),
]

ALL_SERVICE_PRINCIPALS = KNOWN_APPS + SHADOW_APPS


# ---------------------------------------------------------------------------
# Sign-in Logs -- Last 30 days of sign-in activity per app
# ---------------------------------------------------------------------------

def _make_signins(name: str, daily_avg: int, total_users: int,
                  success_rate: float = 0.98, risk_level: str = "none") -> list[dict]:
    """Generate mock sign-in log entries for an app."""
    rng = random.Random(_seed(f"signin-{name}"))
    entries = []
    base_date = datetime(2026, 3, 31)

    for day_offset in range(30):
        date = base_date - timedelta(days=day_offset)
        # Weekend dip
        is_weekend = date.weekday() >= 5
        factor = 0.12 if is_weekend else 1.0
        count = max(0, int(daily_avg * factor * rng.uniform(0.7, 1.3)))

        for _ in range(min(count, 5)):  # Sample up to 5 sign-ins per day
            user_idx = rng.randint(1, total_users)
            success = rng.random() < success_rate
            entries.append({
                "id": _uid(f"signin-{name}-{day_offset}-{user_idx}-{rng.randint(0,999)}"),
                "createdDateTime": (date - timedelta(
                    hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
                )).isoformat() + "Z",
                "appDisplayName": name,
                "appId": _uid(f"sp-{name.lower()}"),
                "userId": _uid(f"user-{user_idx}"),
                "userDisplayName": f"User {user_idx}",
                "userPrincipalName": f"user{user_idx}@contoso.com",
                "ipAddress": f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
                "clientAppUsed": rng.choice(["Browser", "Mobile App", "Desktop Client"]),
                "isInteractive": rng.random() > 0.2,
                "status": {
                    "errorCode": 0 if success else 50076,
                    "failureReason": None if success else "MFA required but not completed",
                },
                "location": {
                    "city": rng.choice(["Minneapolis", "New York", "San Francisco", "London", "Bangalore"]),
                    "state": rng.choice(["MN", "NY", "CA", "LDN", "KA"]),
                    "countryOrRegion": rng.choice(["US", "US", "US", "GB", "IN"]),
                },
                "deviceDetail": {
                    "operatingSystem": rng.choice(["Windows 11", "macOS 14", "iOS 17", "Android 14"]),
                    "browser": rng.choice(["Chrome 122", "Edge 122", "Safari 17", "Firefox 123"]),
                },
                "riskLevelDuringSignIn": risk_level,
                "conditionalAccessStatus": "success" if success else "failure",
                "resourceDisplayName": name,
            })

    return entries


# Pre-generate sign-in data for key apps
_SIGNIN_DATA: dict[str, list[dict]] = {}

# High-usage apps
for _name, _daily, _users in [
    ("Microsoft 365", 9500, 5000), ("Slack", 5200, 4000), ("Microsoft Teams", 8200, 5000),
    ("GitHub Enterprise", 1300, 1000), ("Zoom", 1900, 3000), ("Workday HCM", 1700, 5000),
    ("SAP Concur", 390, 2000), ("CrowdStrike Falcon", 240, 5000), ("Datadog", 660, 1000),
    ("Jira Software", 820, 1000), ("AWS", 1900, 1000),
]:
    _SIGNIN_DATA[_name] = _make_signins(_name, _daily, _users)

# Shadow IT apps (lower volume but present)
for _name, _daily, _users in [
    ("Grammarly Business", 85, 120), ("Calendly", 35, 45),
    ("ChatGPT Enterprise", 280, 350), ("Linear", 45, 30),
    ("Zapier", 60, 50), ("DocuSign", 25, 80),
    ("Canva Enterprise", 40, 65), ("Retool", 15, 12),
]:
    _SIGNIN_DATA[_name] = _make_signins(_name, _daily, _users)

# Low-usage / declining apps
for _name, _daily, _users, _risk in [
    ("Evernote Business", 2, 8, "low"), ("Quip", 3, 15, "none"),
    ("Carbon Black", 9, 45, "none"), ("Webex", 16, 60, "none"),
    ("BlueJeans", 1, 5, "none"), ("Sisense", 8, 30, "none"),
    ("Darktrace", 5, 120, "medium"),
]:
    _SIGNIN_DATA[_name] = _make_signins(_name, _daily, _users, risk_level=_risk)

# Flatten for the signIns endpoint
ALL_SIGNINS = []
for entries in _SIGNIN_DATA.values():
    ALL_SIGNINS.extend(entries)
ALL_SIGNINS.sort(key=lambda x: x["createdDateTime"], reverse=True)


# ---------------------------------------------------------------------------
# Subscribed SKUs -- License inventory
# ---------------------------------------------------------------------------
SUBSCRIBED_SKUS = [
    {
        "id": _uid("sku-m365-e5"),
        "skuId": _uid("sku-id-m365-e5"),
        "skuPartNumber": "ENTERPRISEPREMIUM",
        "displayName": "Microsoft 365 E5",
        "prepaidUnits": {"enabled": 5500, "suspended": 0, "warning": 0},
        "consumedUnits": 4800,
        "appliesTo": "User",
        "servicePlans": [
            {"servicePlanId": _uid("plan-exchange"), "servicePlanName": "EXCHANGE_S_ENTERPRISE", "provisioningStatus": "Success"},
            {"servicePlanId": _uid("plan-teams"), "servicePlanName": "TEAMS1", "provisioningStatus": "Success"},
            {"servicePlanId": _uid("plan-sharepoint"), "servicePlanName": "SHAREPOINTENTERPRISE", "provisioningStatus": "Success"},
            {"servicePlanId": _uid("plan-powerbi"), "servicePlanName": "BI_AZURE_P2", "provisioningStatus": "Success"},
        ],
    },
    {
        "id": _uid("sku-m365-e3"),
        "skuId": _uid("sku-id-m365-e3"),
        "skuPartNumber": "ENTERPRISEPACK",
        "displayName": "Microsoft 365 E3",
        "prepaidUnits": {"enabled": 2000, "suspended": 0, "warning": 200},
        "consumedUnits": 1200,
        "appliesTo": "User",
        "servicePlans": [],
    },
    {
        "id": _uid("sku-powerbi-pro"),
        "skuId": _uid("sku-id-powerbi-pro"),
        "skuPartNumber": "POWER_BI_PRO",
        "displayName": "Power BI Pro",
        "prepaidUnits": {"enabled": 1000, "suspended": 0, "warning": 0},
        "consumedUnits": 850,
        "appliesTo": "User",
        "servicePlans": [],
    },
    {
        "id": _uid("sku-visio"),
        "skuId": _uid("sku-id-visio"),
        "skuPartNumber": "VISIO_PLAN2",
        "displayName": "Visio Plan 2",
        "prepaidUnits": {"enabled": 200, "suspended": 0, "warning": 0},
        "consumedUnits": 45,
        "appliesTo": "User",
        "servicePlans": [],
    },
    {
        "id": _uid("sku-project"),
        "skuId": _uid("sku-id-project"),
        "skuPartNumber": "PROJECT_P1",
        "displayName": "Project Plan 1",
        "prepaidUnits": {"enabled": 150, "suspended": 0, "warning": 0},
        "consumedUnits": 30,
        "appliesTo": "User",
        "servicePlans": [],
    },
    {
        "id": _uid("sku-defender"),
        "skuId": _uid("sku-id-defender"),
        "skuPartNumber": "DEFENDER_ENDPOINT_P2",
        "displayName": "Microsoft Defender for Endpoint P2",
        "prepaidUnits": {"enabled": 5000, "suspended": 0, "warning": 0},
        "consumedUnits": 5000,
        "appliesTo": "User",
        "servicePlans": [],
    },
    {
        "id": _uid("sku-copilot"),
        "skuId": _uid("sku-id-copilot"),
        "skuPartNumber": "MICROSOFT_COPILOT_M365",
        "displayName": "Microsoft 365 Copilot",
        "prepaidUnits": {"enabled": 500, "suspended": 0, "warning": 0},
        "consumedUnits": 180,
        "appliesTo": "User",
        "servicePlans": [],
    },
    {
        "id": _uid("sku-intune"),
        "skuId": _uid("sku-id-intune"),
        "skuPartNumber": "INTUNE_A",
        "displayName": "Microsoft Intune Plan 1",
        "prepaidUnits": {"enabled": 5000, "suspended": 0, "warning": 0},
        "consumedUnits": 4200,
        "appliesTo": "User",
        "servicePlans": [],
    },
]


# ---------------------------------------------------------------------------
# M365 Usage Summary (aggregated report)
# ---------------------------------------------------------------------------
M365_USAGE = {
    "reportDate": "2026-03-31",
    "reportPeriod": "D30",
    "products": [
        {
            "product": "Exchange Online",
            "activeUsers": 4650,
            "totalUsers": 5000,
            "adoptionRate": 93.0,
            "emailsSent": 285000,
            "emailsReceived": 1420000,
            "storageUsedGB": 12400,
        },
        {
            "product": "Microsoft Teams",
            "activeUsers": 4900,
            "totalUsers": 5000,
            "adoptionRate": 98.0,
            "teamChatMessages": 890000,
            "channelMessages": 145000,
            "meetingsOrganized": 42000,
            "meetingMinutes": 2100000,
        },
        {
            "product": "SharePoint Online",
            "activeUsers": 3200,
            "totalUsers": 5000,
            "adoptionRate": 64.0,
            "filesViewed": 180000,
            "filesShared": 45000,
            "storageUsedGB": 8500,
        },
        {
            "product": "OneDrive for Business",
            "activeUsers": 4100,
            "totalUsers": 5000,
            "adoptionRate": 82.0,
            "filesViewed": 320000,
            "filesSynced": 95000,
            "storageUsedGB": 15200,
        },
        {
            "product": "Microsoft 365 Apps",
            "activeUsers": 4500,
            "totalUsers": 5000,
            "adoptionRate": 90.0,
            "wordDocuments": 85000,
            "excelWorkbooks": 120000,
            "powerPointPresentations": 28000,
        },
        {
            "product": "Viva Engage (Yammer)",
            "activeUsers": 420,
            "totalUsers": 5000,
            "adoptionRate": 8.4,
            "messagesPosted": 2800,
            "messagesRead": 18000,
        },
        {
            "product": "Microsoft Copilot",
            "activeUsers": 145,
            "totalUsers": 500,
            "adoptionRate": 29.0,
            "promptsSubmitted": 8500,
            "documentsAssisted": 3200,
        },
    ],
    "licenseUtilization": {
        "totalAssigned": sum(s["consumedUnits"] for s in SUBSCRIBED_SKUS),
        "totalAvailable": sum(s["prepaidUnits"]["enabled"] for s in SUBSCRIBED_SKUS),
        "utilizationRate": round(
            sum(s["consumedUnits"] for s in SUBSCRIBED_SKUS)
            / max(1, sum(s["prepaidUnits"]["enabled"] for s in SUBSCRIBED_SKUS)) * 100, 1
        ),
        "wastedLicenses": sum(
            s["prepaidUnits"]["enabled"] - s["consumedUnits"]
            for s in SUBSCRIBED_SKUS
            if s["consumedUnits"] < s["prepaidUnits"]["enabled"]
        ),
        "estimatedWastedCost": None,  # calculated below
    },
}

# Estimate wasted cost: ~$35/user/month average for M365 E5
_wasted = M365_USAGE["licenseUtilization"]["wastedLicenses"]
M365_USAGE["licenseUtilization"]["estimatedWastedCost"] = _wasted * 35 * 12


# ---------------------------------------------------------------------------
# Graph Intelligence Summary -- pre-computed analysis for the AI prompt
# ---------------------------------------------------------------------------
def _build_intelligence_summary() -> dict:
    """Build a comprehensive summary for AI analysis."""
    shadow_it = [sp for sp in ALL_SERVICE_PRINCIPALS if "shadow-it" in sp.get("tags", [])]
    disabled = [sp for sp in ALL_SERVICE_PRINCIPALS if not sp["accountEnabled"]]

    # Sign-in anomalies: apps with very low usage relative to license count
    low_usage_apps = []
    for name, entries in _SIGNIN_DATA.items():
        unique_users = len(set(e["userId"] for e in entries))
        if unique_users < 20:
            low_usage_apps.append({
                "app": name,
                "unique_users_30d": unique_users,
                "total_signins_30d": len(entries),
            })

    # Risk events
    risky_signins = [s for s in ALL_SIGNINS if s["riskLevelDuringSignIn"] != "none"]

    return {
        "generatedAt": "2026-03-31T23:59:59Z",
        "tenantSummary": {
            "totalServicePrincipals": len(ALL_SERVICE_PRINCIPALS),
            "knownApps": len(KNOWN_APPS),
            "shadowItApps": len(shadow_it),
            "disabledApps": len(disabled),
            "totalSignIns30d": len(ALL_SIGNINS),
            "uniqueUsersSignedIn30d": len(set(s["userId"] for s in ALL_SIGNINS)),
        },
        "shadowItDiscovery": [
            {
                "appName": sp["appDisplayName"],
                "publisher": sp["publisherName"],
                "category": sp["category"],
                "notes": sp["notes"],
                "signInCount30d": len(_SIGNIN_DATA.get(sp["appDisplayName"], [])),
                "uniqueUsers30d": len(set(
                    e["userId"] for e in _SIGNIN_DATA.get(sp["appDisplayName"], [])
                )),
            }
            for sp in shadow_it
        ],
        "lowUsageAlerts": low_usage_apps,
        "riskySummary": {
            "totalRiskySignIns": len(risky_signins),
            "byRiskLevel": {
                "low": sum(1 for s in risky_signins if s["riskLevelDuringSignIn"] == "low"),
                "medium": sum(1 for s in risky_signins if s["riskLevelDuringSignIn"] == "medium"),
                "high": sum(1 for s in risky_signins if s["riskLevelDuringSignIn"] == "high"),
            },
        },
        "licenseWaste": {
            "totalWastedLicenses": M365_USAGE["licenseUtilization"]["wastedLicenses"],
            "estimatedAnnualWaste": M365_USAGE["licenseUtilization"]["estimatedWastedCost"],
            "topWaste": [
                {
                    "sku": s["displayName"],
                    "assigned": s["consumedUnits"],
                    "available": s["prepaidUnits"]["enabled"],
                    "unused": s["prepaidUnits"]["enabled"] - s["consumedUnits"],
                    "utilizationPct": round(s["consumedUnits"] / max(1, s["prepaidUnits"]["enabled"]) * 100, 1),
                }
                for s in sorted(SUBSCRIBED_SKUS,
                                key=lambda x: x["prepaidUnits"]["enabled"] - x["consumedUnits"],
                                reverse=True)[:5]
            ],
        },
        "m365Adoption": [
            {
                "product": p["product"],
                "activeUsers": p["activeUsers"],
                "totalUsers": p["totalUsers"],
                "adoptionRate": p["adoptionRate"],
            }
            for p in M365_USAGE["products"]
        ],
    }


INTELLIGENCE_SUMMARY = _build_intelligence_summary()


# ===========================================================================
# API Endpoints -- Mimic Microsoft Graph v1.0 structure
# ===========================================================================

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-graph"}


# ---------------------------------------------------------------------------
# Service Principals (App Discovery)
# ---------------------------------------------------------------------------

@app.get("/v1.0/servicePrincipals")
async def list_service_principals(
    top: int = Query(100, alias="$top", ge=1, le=999),
    skip: int = Query(0, alias="$skip", ge=0),
    filter: Optional[str] = Query(None, alias="$filter"),
    search: Optional[str] = Query(None, alias="$search"),
):
    """List enterprise application service principals."""
    results = ALL_SERVICE_PRINCIPALS

    # Simple filter support
    if filter:
        if "tags/any" in filter and "shadow-it" in filter:
            results = [sp for sp in results if "shadow-it" in sp.get("tags", [])]
        elif "accountEnabled eq false" in filter:
            results = [sp for sp in results if not sp["accountEnabled"]]
        elif "accountEnabled eq true" in filter:
            results = [sp for sp in results if sp["accountEnabled"]]

    if search:
        q = search.strip('"').lower()
        results = [sp for sp in results if q in sp["appDisplayName"].lower()
                   or q in sp.get("publisherName", "").lower()]

    total = len(results)
    page = results[skip:skip + top]

    return {
        "@odata.count": total,
        "@odata.nextLink": f"/v1.0/servicePrincipals?$top={top}&$skip={skip + top}" if skip + top < total else None,
        "value": page,
    }


@app.get("/v1.0/servicePrincipals/{sp_id}")
async def get_service_principal(sp_id: str):
    for sp in ALL_SERVICE_PRINCIPALS:
        if sp["id"] == sp_id or sp["appId"] == sp_id:
            return sp
    return {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}}


# ---------------------------------------------------------------------------
# Audit Logs / Sign-Ins
# ---------------------------------------------------------------------------

@app.get("/v1.0/auditLogs/signIns")
async def list_signins(
    top: int = Query(50, alias="$top", ge=1, le=1000),
    skip: int = Query(0, alias="$skip", ge=0),
    filter: Optional[str] = Query(None, alias="$filter"),
):
    """List sign-in activity logs."""
    results = ALL_SIGNINS

    if filter:
        if "appDisplayName eq" in filter:
            app_name = filter.split("'")[1] if "'" in filter else ""
            results = [s for s in results if s["appDisplayName"] == app_name]
        elif "riskLevelDuringSignIn ne" in filter and "'none'" in filter:
            results = [s for s in results if s["riskLevelDuringSignIn"] != "none"]

    total = len(results)
    page = results[skip:skip + top]

    return {
        "@odata.count": total,
        "value": page,
    }


# ---------------------------------------------------------------------------
# Subscribed SKUs (License Management)
# ---------------------------------------------------------------------------

@app.get("/v1.0/subscribedSkus")
async def list_subscribed_skus():
    """List all subscribed license SKUs."""
    return {"value": SUBSCRIBED_SKUS}


# ---------------------------------------------------------------------------
# M365 Usage Reports
# ---------------------------------------------------------------------------

@app.get("/v1.0/reports/m365Usage")
async def m365_usage_report():
    """Aggregated Microsoft 365 usage report."""
    return M365_USAGE


# ---------------------------------------------------------------------------
# Graph Intelligence (Custom summary endpoint for AI analysis)
# ---------------------------------------------------------------------------

@app.get("/v1.0/intelligence/summary")
async def intelligence_summary():
    """Pre-computed intelligence summary for AI-powered analysis.

    This is a custom endpoint (not in real Graph API) that aggregates
    data across all Graph resources into a single payload optimized
    for the TechDebt AI rationalization engine.
    """
    return INTELLIGENCE_SUMMARY
