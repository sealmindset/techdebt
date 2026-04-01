"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import type { DashboardStats } from "@/lib/types";
import {
  LayoutDashboard,
  DollarSign,
  Users,
  PiggyBank,
  TrendingDown,
  ArrowRight,
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

export default function DashboardPage() {
  const { authMe, hasPermission } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    apiGet<DashboardStats>("/dashboard")
      .then(setStats)
      .catch((err) => console.error("Failed to load dashboard:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div
          className="h-8 w-48 animate-pulse rounded"
          style={{ backgroundColor: "var(--muted)" }}
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-28 animate-pulse rounded-xl border"
              style={{
                backgroundColor: "var(--card)",
                borderColor: "var(--border)",
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p style={{ color: "var(--muted-foreground)" }}>
          Welcome to TechDebt{authMe?.name ? `, ${authMe.name}` : ""}. Your SaaS rationalization overview.
        </p>
      </div>

      {stats ? (
        <>
          {/* Stats cards row */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                label: "Total Applications",
                value: stats.total_apps.toLocaleString(),
                icon: LayoutDashboard,
                color: "var(--primary)",
              },
              {
                label: "Total Annual Spend",
                value: currencyFmt.format(stats.total_spend),
                icon: DollarSign,
                color: "var(--muted-foreground)",
              },
              {
                label: "Avg Adoption Rate",
                value: percentFmt.format(stats.avg_adoption_rate / 100),
                icon: Users,
                color: "var(--primary)",
              },
              {
                label: "Potential Savings",
                value: currencyFmt.format(stats.total_potential_savings),
                icon: PiggyBank,
                color: "var(--success, var(--primary))",
              },
            ].map(({ label, value, icon: Icon, color }) => (
              <div
                key={label}
                className="rounded-xl border p-6"
                style={{
                  backgroundColor: "var(--card)",
                  borderColor: "var(--border)",
                  color: "var(--card-foreground)",
                }}
              >
                <div className="flex items-center justify-between">
                  <p
                    className="text-sm font-medium"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    {label}
                  </p>
                  <Icon className="h-4 w-4" style={{ color }} />
                </div>
                <p className="mt-2 text-2xl font-bold">{value}</p>
              </div>
            ))}
          </div>

          {/* Recommendation breakdown + Apps by Category */}
          <div className="grid gap-4 lg:grid-cols-2">
            {/* Recommendation breakdown */}
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
                Breakdown by recommendation type.
              </p>
              <div className="mt-4 grid grid-cols-2 gap-3">
                {(["keep", "cut", "replace", "consolidate"] as const).map(
                  (type) => {
                    const count = stats.recommendations_summary[type] || 0;
                    const colors = REC_TYPE_COLORS[type];
                    return (
                      <div
                        key={type}
                        className="rounded-lg p-4 text-center"
                        style={{ backgroundColor: colors.bg }}
                      >
                        <p
                          className="text-2xl font-bold"
                          style={{ color: colors.fg }}
                        >
                          {count}
                        </p>
                        <p
                          className="mt-1 text-sm font-medium capitalize"
                          style={{ color: colors.fg }}
                        >
                          {type}
                        </p>
                      </div>
                    );
                  }
                )}
              </div>
            </div>

            {/* Apps by category */}
            <div
              className="rounded-xl border p-6"
              style={{
                backgroundColor: "var(--card)",
                borderColor: "var(--border)",
                color: "var(--card-foreground)",
              }}
            >
              <h2 className="text-lg font-semibold">Apps by Category</h2>
              <p
                className="mt-1 text-sm"
                style={{ color: "var(--muted-foreground)" }}
              >
                Distribution across categories.
              </p>
              <div className="mt-4 space-y-3">
                {Object.entries(stats.apps_by_category)
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, count]) => {
                    const maxCount = Math.max(
                      ...Object.values(stats.apps_by_category)
                    );
                    const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    return (
                      <div key={category}>
                        <div className="flex items-center justify-between text-sm">
                          <span>{category}</span>
                          <span
                            className="font-medium"
                            style={{ color: "var(--muted-foreground)" }}
                          >
                            {count}
                          </span>
                        </div>
                        <div
                          className="mt-1 h-2 w-full rounded-full"
                          style={{
                            backgroundColor:
                              "color-mix(in oklch, var(--primary) 15%, transparent)",
                          }}
                        >
                          <div
                            className="h-2 rounded-full"
                            style={{
                              width: `${pct}%`,
                              backgroundColor: "var(--primary)",
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>

          {/* Top savings opportunities */}
          {stats.top_savings_opportunities.length > 0 && (
            <div
              className="rounded-xl border p-6"
              style={{
                backgroundColor: "var(--card)",
                borderColor: "var(--border)",
                color: "var(--card-foreground)",
              }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold">
                    Top Savings Opportunities
                  </h2>
                  <p
                    className="mt-1 text-sm"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    Applications with the highest potential cost savings.
                  </p>
                </div>
                {hasPermission("applications", "read") && (
                  <button
                    onClick={() => router.push("/applications")}
                    className="inline-flex items-center gap-1 text-sm font-medium"
                    style={{ color: "var(--primary)" }}
                  >
                    View all
                    <ArrowRight className="h-4 w-4" />
                  </button>
                )}
              </div>
              <div className="mt-4 overflow-x-auto rounded-md border" style={{ borderColor: "var(--border)" }}>
                <table className="w-full text-sm">
                  <thead>
                    <tr
                      className="border-b"
                      style={{ borderColor: "var(--border)" }}
                    >
                      <th
                        className="h-10 px-3 text-left font-medium"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        Application
                      </th>
                      <th
                        className="h-10 px-3 text-left font-medium"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        Vendor
                      </th>
                      <th
                        className="h-10 px-3 text-left font-medium"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        Type
                      </th>
                      <th
                        className="h-10 px-3 text-right font-medium"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        Annual Cost
                      </th>
                      <th
                        className="h-10 px-3 text-right font-medium"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        Potential Savings
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.top_savings_opportunities.map((opp) => {
                      const colors =
                        REC_TYPE_COLORS[opp.recommendation_type] ||
                        REC_TYPE_COLORS.keep;
                      return (
                        <tr
                          key={opp.id}
                          className="border-b transition-colors hover:bg-muted/50 cursor-pointer"
                          style={{ borderColor: "var(--border)" }}
                          onClick={() => router.push(`/applications/${opp.id}`)}
                        >
                          <td className="px-3 py-2.5 font-medium">
                            {opp.name}
                          </td>
                          <td
                            className="px-3 py-2.5"
                            style={{ color: "var(--muted-foreground)" }}
                          >
                            {opp.vendor}
                          </td>
                          <td className="px-3 py-2.5">
                            <span
                              className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize"
                              style={{
                                backgroundColor: colors.bg,
                                color: colors.fg,
                              }}
                            >
                              {opp.recommendation_type}
                            </span>
                          </td>
                          <td className="px-3 py-2.5 text-right">
                            {currencyFmt.format(opp.annual_cost)}
                          </td>
                          <td className="px-3 py-2.5 text-right font-medium">
                            <span className="inline-flex items-center gap-1">
                              <TrendingDown
                                className="h-3.5 w-3.5"
                                style={{
                                  color:
                                    "var(--success, var(--primary))",
                                }}
                              />
                              {currencyFmt.format(opp.savings_estimate)}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Recent decisions */}
          {stats.recent_decisions.length > 0 && (
            <div
              className="rounded-xl border p-6"
              style={{
                backgroundColor: "var(--card)",
                borderColor: "var(--border)",
                color: "var(--card-foreground)",
              }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold">Recent Decisions</h2>
                  <p
                    className="mt-1 text-sm"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    Latest rationalization decisions.
                  </p>
                </div>
                {hasPermission("decisions", "read") && (
                  <button
                    onClick={() => router.push("/decisions")}
                    className="inline-flex items-center gap-1 text-sm font-medium"
                    style={{ color: "var(--primary)" }}
                  >
                    View all
                    <ArrowRight className="h-4 w-4" />
                  </button>
                )}
              </div>
              <div className="mt-4 space-y-3">
                {stats.recent_decisions.map((d) => {
                  const colors =
                    DECISION_STATUS_COLORS[d.status] ||
                    DECISION_STATUS_COLORS.pending_review;
                  return (
                    <div
                      key={d.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                      style={{ borderColor: "var(--border)" }}
                    >
                      <div>
                        <p className="font-medium">{d.application_name}</p>
                        <p
                          className="text-sm"
                          style={{ color: "var(--muted-foreground)" }}
                        >
                          {d.decision_type} by {d.submitted_by}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                          style={{
                            backgroundColor: colors.bg,
                            color: colors.fg,
                          }}
                        >
                          {d.status.replace(/_/g, " ")}
                        </span>
                        <span
                          className="text-xs"
                          style={{ color: "var(--muted-foreground)" }}
                        >
                          {formatDate(d.created_at)}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      ) : (
        <p style={{ color: "var(--muted-foreground)" }}>
          Failed to load dashboard data.
        </p>
      )}
    </div>
  );
}
