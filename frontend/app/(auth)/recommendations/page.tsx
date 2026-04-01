"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { type ColumnDef } from "@tanstack/react-table";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { DataTableColumnHeader } from "@/components/data-table-column-header";
import { formatDate } from "@/lib/utils";
import type { Recommendation } from "@/lib/types";

const currencyFmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
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

const STATUS_COLORS: Record<string, { bg: string; fg: string }> = {
  pending: {
    bg: "color-mix(in oklch, var(--warning, var(--primary)) 15%, transparent)",
    fg: "var(--warning, var(--primary))",
  },
  accepted: {
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

export default function RecommendationsPage() {
  const { hasPermission } = useAuth();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchRecommendations = useCallback(async () => {
    try {
      const data = await apiGet<Recommendation[]>("/recommendations");
      setRecommendations(data);
    } catch (err) {
      console.error("Failed to load recommendations:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  const columns: ColumnDef<Recommendation, unknown>[] = [
    {
      accessorKey: "application",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Application" />
      ),
      accessorFn: (row) => row.application_name || row.application?.name || "-",
      cell: ({ row }) => (
        <span className="font-medium">
          {row.original.application_name || row.original.application?.name || "-"}
        </span>
      ),
    },
    {
      accessorKey: "recommendation_type",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Type" />
      ),
      cell: ({ row }) => {
        const type = row.original.recommendation_type;
        const colors = REC_TYPE_COLORS[type] || REC_TYPE_COLORS.keep;
        return (
          <span
            className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize"
            style={{ backgroundColor: colors.bg, color: colors.fg }}
          >
            {type}
          </span>
        );
      },
      filterFn: (row, id, value: string[]) => {
        return value.includes(String(row.getValue(id)));
      },
    },
    {
      accessorKey: "confidence_score",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Confidence" />
      ),
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <div
            className="h-2 w-16 rounded-full"
            style={{
              backgroundColor:
                "color-mix(in oklch, var(--primary) 15%, transparent)",
            }}
          >
            <div
              className="h-2 rounded-full"
              style={{
                width: `${row.original.confidence_score}%`,
                backgroundColor: "var(--primary)",
              }}
            />
          </div>
          <span className="text-sm tabular-nums">
            {row.original.confidence_score}%
          </span>
        </div>
      ),
    },
    {
      accessorKey: "cost_savings_estimate",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Savings Estimate" />
      ),
      cell: ({ row }) => (
        <span className="font-medium tabular-nums">
          {currencyFmt.format(row.original.cost_savings_estimate ?? 0)}
        </span>
      ),
    },
    {
      accessorKey: "alternative_app",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Alternative" />
      ),
      cell: ({ row }) => (
        <span style={{ color: "var(--muted-foreground)" }}>
          {row.original.alternative_app || "-"}
        </span>
      ),
    },
    {
      accessorKey: "status",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Status" />
      ),
      cell: ({ row }) => {
        const status = row.original.status;
        const colors = STATUS_COLORS[status] || STATUS_COLORS.pending;
        return (
          <span
            className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize"
            style={{ backgroundColor: colors.bg, color: colors.fg }}
          >
            {status.replace(/_/g, " ")}
          </span>
        );
      },
      filterFn: (row, id, value: string[]) => {
        return value.includes(String(row.getValue(id)));
      },
    },
    {
      accessorKey: "created_at",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Created" />
      ),
      cell: ({ row }) => formatDate(row.original.created_at),
    },
  ];

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

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Recommendations</h1>
        <p style={{ color: "var(--muted-foreground)" }}>
          AI-generated rationalization recommendations for all tracked
          applications.
        </p>
      </div>

      {/* Recommendations data table */}
      <DataTable
        columns={columns}
        data={recommendations}
        storageKey="recommendations-table"
        searchKey="application"
        searchPlaceholder="Search by application..."
        onRowClick={(rec) =>
          rec.application_id &&
          router.push(`/applications/${rec.application_id}`)
        }
      />
    </div>
  );
}
