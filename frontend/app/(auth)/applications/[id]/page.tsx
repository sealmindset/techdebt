"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import type { Application, Recommendation, Decision } from "@/lib/types";
import {
  ArrowLeft,
  DollarSign,
  Users,
  TrendingUp,
  AlertTriangle,
  ShieldCheck,
  Calendar,
} from "lucide-react";

const currencyFmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percentFmt = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

const STATUS_COLORS: Record<string, { bg: string; fg: string }> = {
  active: {
    bg: "color-mix(in oklch, var(--success, var(--primary)) 15%, transparent)",
    fg: "var(--success, var(--primary))",
  },
  under_review: {
    bg: "color-mix(in oklch, var(--warning, var(--primary)) 15%, transparent)",
    fg: "var(--warning, var(--primary))",
  },
  deprecated: {
    bg: "color-mix(in oklch, var(--destructive) 15%, transparent)",
    fg: "var(--destructive)",
  },
  retired: {
    bg: "color-mix(in oklch, var(--muted-foreground) 15%, transparent)",
    fg: "var(--muted-foreground)",
  },
};

const REC_TYPE_COLORS: Record<string, { bg: string; fg: string }> = {
  keep: {
    bg: "color-mix(in oklch, var(--success, var(--primary)) 15%, transparent)",
    fg: "var(--success, var(--primary))",
  },
  cut: {
    bg: "color-mix(in oklch, var(--destructive) 15%, transparent)",
    fg: "var(--destructive)",
  },
  replace: {
    bg: "color-mix(in oklch, var(--warning, var(--primary)) 15%, transparent)",
    fg: "var(--warning, var(--primary))",
  },
  consolidate: {
    bg: "color-mix(in oklch, var(--primary) 15%, transparent)",
    fg: "var(--primary)",
  },
};

const DECISION_STATUS_COLORS: Record<string, { bg: string; fg: string }> = {
  pending_review: {
    bg: "color-mix(in oklch, var(--warning, var(--primary)) 15%, transparent)",
    fg: "var(--warning, var(--primary))",
  },
  approved: {
    bg: "color-mix(in oklch, var(--success, var(--primary)) 15%, transparent)",
    fg: "var(--success, var(--primary))",
  },
  rejected: {
    bg: "color-mix(in oklch, var(--destructive) 15%, transparent)",
    fg: "var(--destructive)",
  },
  implemented: {
    bg: "color-mix(in oklch, var(--primary) 15%, transparent)",
    fg: "var(--primary)",
  },
};

function riskColor(score: number): string {
  if (score >= 70) return "var(--destructive)";
  if (score >= 40) return "var(--warning, var(--primary))";
  return "var(--success, var(--primary))";
}

function complianceColor(status: string): { bg: string; fg: string } {
  if (status === "compliant") {
    return {
      bg: "color-mix(in oklch, var(--success, var(--primary)) 15%, transparent)",
      fg: "var(--success, var(--primary))",
    };
  }
  if (status === "non_compliant") {
    return {
      bg: "color-mix(in oklch, var(--destructive) 15%, transparent)",
      fg: "var(--destructive)",
    };
  }
  return {
    bg: "color-mix(in oklch, var(--warning, var(--primary)) 15%, transparent)",
    fg: "var(--warning, var(--primary))",
  };
}

export default function ApplicationDetailPage() {
  const { hasPermission } = useAuth();
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [app, setApp] = useState<Application | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [appData, recsData, decsData] = await Promise.all([
        apiGet<Application>(`/applications/${id}`),
        apiGet<Recommendation[]>(`/applications/${id}/recommendations`),
        apiGet<Decision[]>(`/applications/${id}/decisions`),
      ]);
      setApp(appData);
      setRecommendations(recsData);
      setDecisions(decsData);
    } catch (err) {
      console.error("Failed to load application:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div
          className="h-8 w-48 animate-pulse rounded"
          style={{ backgroundColor: "var(--muted)" }}
        />
        <div
          className="h-64 animate-pulse rounded-xl border"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
          }}
        />
      </div>
    );
  }

  if (!app) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => router.push("/applications")}
          className="inline-flex items-center gap-1 text-sm"
          style={{ color: "var(--muted-foreground)" }}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Applications
        </button>
        <p style={{ color: "var(--muted-foreground)" }}>
          Application not found.
        </p>
      </div>
    );
  }

  const statusColors = STATUS_COLORS[app.status] || STATUS_COLORS.active;
  const compColors = complianceColor(app.compliance_status ?? "unknown");

  return (
    <div className="space-y-6">
      {/* Back link */}
      <button
        onClick={() => router.push("/applications")}
        className="inline-flex items-center gap-1 text-sm transition-colors"
        style={{ color: "var(--muted-foreground)" }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = "var(--foreground)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = "var(--muted-foreground)";
        }}
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Applications
      </button>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{app.name}</h1>
            <span
              className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize"
              style={{
                backgroundColor: statusColors.bg,
                color: statusColors.fg,
              }}
            >
              {app.status.replace(/_/g, " ")}
            </span>
          </div>
          <p style={{ color: "var(--muted-foreground)" }}>
            {app.vendor} &middot; {app.category} &middot; {app.department}
          </p>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {[
          {
            label: "Annual Cost",
            value: currencyFmt.format(app.annual_cost),
            icon: DollarSign,
            color: "var(--muted-foreground)",
          },
          {
            label: "Cost Per License",
            value: currencyFmt.format(app.cost_per_license ?? 0),
            icon: DollarSign,
            color: "var(--muted-foreground)",
          },
          {
            label: "Active Users",
            value: `${(app.active_users ?? 0).toLocaleString()} / ${(app.total_licenses ?? 0).toLocaleString()}`,
            icon: Users,
            color: "var(--primary)",
          },
          {
            label: "Adoption Rate",
            value: percentFmt.format((app.adoption_rate ?? 0) / 100),
            icon: TrendingUp,
            color: "var(--primary)",
          },
          {
            label: "Risk Score",
            value: String(app.risk_score ?? "N/A"),
            icon: AlertTriangle,
            color: riskColor(app.risk_score),
          },
        ].map(({ label, value, icon: Icon, color }) => (
          <div
            key={label}
            className="rounded-xl border p-4"
            style={{
              backgroundColor: "var(--card)",
              borderColor: "var(--border)",
              color: "var(--card-foreground)",
            }}
          >
            <div className="flex items-center justify-between">
              <p
                className="text-xs font-medium"
                style={{ color: "var(--muted-foreground)" }}
              >
                {label}
              </p>
              <Icon className="h-4 w-4" style={{ color }} />
            </div>
            <p className="mt-1 text-xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      {/* Info grid: Compliance, Contract, Description */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Compliance */}
        <div
          className="rounded-xl border p-5"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--card-foreground)",
          }}
        >
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5" style={{ color: compColors.fg }} />
            <h3 className="font-semibold">Compliance</h3>
          </div>
          <div className="mt-3">
            <span
              className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize"
              style={{
                backgroundColor: compColors.bg,
                color: compColors.fg,
              }}
            >
              {(app.compliance_status ?? "unknown").replace(/_/g, " ")}
            </span>
          </div>
        </div>

        {/* Contract dates */}
        <div
          className="rounded-xl border p-5"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--card-foreground)",
          }}
        >
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5" style={{ color: "var(--primary)" }} />
            <h3 className="font-semibold">Contract</h3>
          </div>
          <div className="mt-3 space-y-2">
            <div className="flex justify-between text-sm">
              <span style={{ color: "var(--muted-foreground)" }}>Start</span>
              <span className="font-medium">
                {formatDate(app.contract_start)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span style={{ color: "var(--muted-foreground)" }}>End</span>
              <span className="font-medium">
                {formatDate(app.contract_end)}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        <div
          className="rounded-xl border p-5"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--card-foreground)",
          }}
        >
          <h3 className="font-semibold">Description</h3>
          <p
            className="mt-2 text-sm"
            style={{ color: "var(--muted-foreground)" }}
          >
            {app.description || "No description available."}
          </p>
        </div>
      </div>

      {/* Recommendations */}
      <div
        className="rounded-xl border p-6"
        style={{
          backgroundColor: "var(--card)",
          borderColor: "var(--border)",
          color: "var(--card-foreground)",
        }}
      >
        <h2 className="text-lg font-semibold">Recommendations</h2>
        <p
          className="mt-1 text-sm"
          style={{ color: "var(--muted-foreground)" }}
        >
          AI-generated rationalization recommendations for this application.
        </p>

        {recommendations.length === 0 ? (
          <p
            className="mt-4 text-sm"
            style={{ color: "var(--muted-foreground)" }}
          >
            No recommendations yet.
          </p>
        ) : (
          <div className="mt-4 space-y-3">
            {recommendations.map((rec) => {
              const recColors =
                REC_TYPE_COLORS[rec.recommendation_type] || REC_TYPE_COLORS.keep;
              return (
                <div
                  key={rec.id}
                  className="rounded-lg border p-4"
                  style={{ borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                        style={{
                          backgroundColor: recColors.bg,
                          color: recColors.fg,
                        }}
                      >
                        {rec.recommendation_type}
                      </span>
                      <span
                        className="text-sm"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        Confidence: {rec.confidence_score}%
                      </span>
                    </div>
                    <span className="text-sm font-medium">
                      {currencyFmt.format(rec.cost_savings_estimate ?? 0)} savings
                    </span>
                  </div>
                  <p className="mt-2 text-sm">{rec.reasoning}</p>
                  {rec.alternative_app && (
                    <p
                      className="mt-1 text-sm"
                      style={{ color: "var(--muted-foreground)" }}
                    >
                      Alternative: {rec.alternative_app}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Decisions */}
      <div
        className="rounded-xl border p-6"
        style={{
          backgroundColor: "var(--card)",
          borderColor: "var(--border)",
          color: "var(--card-foreground)",
        }}
      >
        <h2 className="text-lg font-semibold">Decisions</h2>
        <p
          className="mt-1 text-sm"
          style={{ color: "var(--muted-foreground)" }}
        >
          Rationalization decisions for this application.
        </p>

        {decisions.length === 0 ? (
          <p
            className="mt-4 text-sm"
            style={{ color: "var(--muted-foreground)" }}
          >
            No decisions yet.
          </p>
        ) : (
          <div className="mt-4 space-y-3">
            {decisions.map((dec) => {
              const decColors =
                DECISION_STATUS_COLORS[dec.status] ||
                DECISION_STATUS_COLORS.pending_review;
              return (
                <div
                  key={dec.id}
                  className="rounded-lg border p-4"
                  style={{ borderColor: "var(--border)" }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{dec.decision_type}</span>
                      <span
                        className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                        style={{
                          backgroundColor: decColors.bg,
                          color: decColors.fg,
                        }}
                      >
                        {dec.status.replace(/_/g, " ")}
                      </span>
                    </div>
                    <span
                      className="text-sm"
                      style={{ color: "var(--muted-foreground)" }}
                    >
                      {formatDate(dec.created_at)}
                    </span>
                  </div>
                  <p className="mt-2 text-sm">{dec.justification}</p>
                  <div
                    className="mt-2 flex items-center gap-4 text-xs"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    <span>By: {dec.submitter_name || dec.submitted_by}</span>
                    <span>
                      Cost impact: {currencyFmt.format(dec.cost_impact ?? 0)}
                    </span>
                  </div>
                  {dec.review_notes && (
                    <p
                      className="mt-2 rounded-md p-2 text-sm"
                      style={{
                        backgroundColor:
                          "color-mix(in oklch, var(--muted) 50%, transparent)",
                        color: "var(--muted-foreground)",
                      }}
                    >
                      Review: {dec.review_notes}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
