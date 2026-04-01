"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { type ColumnDef } from "@tanstack/react-table";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { DataTableColumnHeader } from "@/components/data-table-column-header";
import { formatDate } from "@/lib/utils";
import type { Decision } from "@/lib/types";

const currencyFmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const STATUS_COLORS: Record<string, { bg: string; fg: string }> = {
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

export default function DecisionsPage() {
  const { hasPermission } = useAuth();
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchDecisions = useCallback(async () => {
    try {
      const data = await apiGet<Decision[]>("/decisions");
      setDecisions(data);
    } catch (err) {
      console.error("Failed to load decisions:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDecisions();
  }, [fetchDecisions]);

  const columns: ColumnDef<Decision, unknown>[] = [
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
      accessorKey: "decision_type",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Decision Type" />
      ),
      cell: ({ row }) => (
        <span className="capitalize">
          {row.original.decision_type.replace(/_/g, " ")}
        </span>
      ),
      filterFn: (row, id, value: string[]) => {
        return value.includes(String(row.getValue(id)));
      },
    },
    {
      accessorKey: "submitted_by",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Submitted By" />
      ),
      accessorFn: (row) => row.submitter_name || row.submitted_by,
      cell: ({ row }) => (
        <span>{row.original.submitter_name || row.original.submitted_by}</span>
      ),
    },
    {
      accessorKey: "status",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Status" />
      ),
      cell: ({ row }) => {
        const status = row.original.status;
        const colors = STATUS_COLORS[status] || STATUS_COLORS.pending_review;
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
      accessorKey: "cost_impact",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Cost Impact" />
      ),
      cell: ({ row }) => {
        const impact = row.original.cost_impact ?? 0;
        const isNegative = impact < 0;
        return (
          <span
            className="font-medium tabular-nums"
            style={{
              color: isNegative
                ? "var(--success, var(--primary))"
                : "var(--foreground)",
            }}
          >
            {currencyFmt.format(impact)}
          </span>
        );
      },
    },
    {
      accessorKey: "justification",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Justification" />
      ),
      cell: ({ row }) => (
        <span
          className="line-clamp-1 max-w-[300px] text-sm"
          title={row.original.justification}
          style={{ color: "var(--muted-foreground)" }}
        >
          {row.original.justification}
        </span>
      ),
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
        <h1 className="text-2xl font-bold tracking-tight">Decisions</h1>
        <p style={{ color: "var(--muted-foreground)" }}>
          Rationalization decisions submitted for review and approval.
        </p>
      </div>

      {/* Decisions data table */}
      <DataTable
        columns={columns}
        data={decisions}
        storageKey="decisions-table"
        searchKey="application"
        searchPlaceholder="Search by application..."
        onRowClick={(dec) =>
          dec.application_id &&
          router.push(`/applications/${dec.application_id}`)
        }
      />
    </div>
  );
}
