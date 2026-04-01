"use client";

import { useEffect, useState, useCallback } from "react";
import { type ColumnDef } from "@tanstack/react-table";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { DataTableColumnHeader } from "@/components/data-table-column-header";
import { formatDate } from "@/lib/utils";
import type { Submission } from "@/lib/types";

const currencyFmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const STATUS_COLORS: Record<string, { bg: string; fg: string }> = {
  pending: {
    bg: "color-mix(in oklch, var(--warning, var(--primary)) 15%, transparent)",
    fg: "var(--warning, var(--primary))",
  },
  matched: {
    bg: "color-mix(in oklch, var(--success, var(--primary)) 15%, transparent)",
    fg: "var(--success, var(--primary))",
  },
  new_app: {
    bg: "color-mix(in oklch, var(--primary) 15%, transparent)",
    fg: "var(--primary)",
  },
  rejected: {
    bg: "color-mix(in oklch, var(--destructive) 15%, transparent)",
    fg: "var(--destructive)",
  },
};

export default function SubmissionsPage() {
  const { hasPermission } = useAuth();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSubmissions = useCallback(async () => {
    try {
      const data = await apiGet<Submission[]>("/submissions");
      setSubmissions(data);
    } catch (err) {
      console.error("Failed to load submissions:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  const columns: ColumnDef<Submission, unknown>[] = [
    {
      accessorKey: "app_name",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="App Name" />
      ),
      cell: ({ row }) => (
        <span className="font-medium">{row.original.app_name}</span>
      ),
    },
    {
      accessorKey: "vendor",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Vendor" />
      ),
    },
    {
      accessorKey: "department",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Department" />
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
    },
    {
      accessorKey: "usage_frequency",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Usage" />
      ),
      cell: ({ row }) => (
        <span className="capitalize">
          {row.original.usage_frequency.replace(/_/g, " ")}
        </span>
      ),
      filterFn: (row, id, value: string[]) => {
        return value.includes(String(row.getValue(id)));
      },
    },
    {
      accessorKey: "user_count",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Users" />
      ),
      cell: ({ row }) => (
        <span className="tabular-nums">
          {row.original.user_count.toLocaleString()}
        </span>
      ),
    },
    {
      accessorKey: "estimated_cost",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Est. Cost" />
      ),
      cell: ({ row }) => (
        <span className="font-medium tabular-nums">
          {currencyFmt.format(row.original.estimated_cost)}
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
        <DataTableColumnHeader column={column} title="Submitted" />
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
        <h1 className="text-2xl font-bold tracking-tight">Submissions</h1>
        <p style={{ color: "var(--muted-foreground)" }}>
          Voluntary application submissions from teams across the organization.
        </p>
      </div>

      {/* Submissions data table */}
      <DataTable
        columns={columns}
        data={submissions}
        storageKey="submissions-table"
        searchKey="app_name"
        searchPlaceholder="Search submissions..."
      />
    </div>
  );
}
