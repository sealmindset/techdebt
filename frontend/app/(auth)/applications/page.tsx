"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { type ColumnDef } from "@tanstack/react-table";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DataTable } from "@/components/data-table";
import { DataTableColumnHeader } from "@/components/data-table-column-header";
import { formatDate } from "@/lib/utils";
import type { Application } from "@/lib/types";

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

function riskColor(score: number): string {
  if (score >= 70) return "var(--destructive)";
  if (score >= 40) return "var(--warning, var(--primary))";
  return "var(--success, var(--primary))";
}

export default function ApplicationsPage() {
  const { hasPermission } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const canRead = hasPermission("applications", "read");

  const fetchApplications = useCallback(async () => {
    try {
      const data = await apiGet<Application[]>("/applications");
      setApplications(data);
    } catch (err) {
      console.error("Failed to load applications:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  const columns: ColumnDef<Application, unknown>[] = [
    {
      accessorKey: "name",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Name" />
      ),
      cell: ({ row }) => (
        <span className="font-medium">{row.original.name}</span>
      ),
    },
    {
      accessorKey: "vendor",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Vendor" />
      ),
    },
    {
      accessorKey: "category",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Category" />
      ),
      filterFn: (row, id, value: string[]) => {
        return value.includes(String(row.getValue(id)));
      },
    },
    {
      accessorKey: "status",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Status" />
      ),
      cell: ({ row }) => {
        const status = row.original.status;
        const colors = STATUS_COLORS[status] || STATUS_COLORS.active;
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
      accessorKey: "annual_cost",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Annual Cost" />
      ),
      cell: ({ row }) => (
        <span className="text-right font-medium tabular-nums">
          {currencyFmt.format(row.original.annual_cost)}
        </span>
      ),
    },
    {
      accessorKey: "active_users",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Active Users" />
      ),
      cell: ({ row }) => (
        <span className="tabular-nums">
          {row.original.active_users.toLocaleString()}
        </span>
      ),
    },
    {
      accessorKey: "adoption_rate",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Adoption" />
      ),
      cell: ({ row }) => (
        <span className="tabular-nums">
          {percentFmt.format(row.original.adoption_rate / 100)}
        </span>
      ),
    },
    {
      accessorKey: "risk_score",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Risk" />
      ),
      cell: ({ row }) => {
        const score = row.original.risk_score;
        return (
          <span
            className="font-medium tabular-nums"
            style={{ color: riskColor(score) }}
          >
            {score}
          </span>
        );
      },
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
        <h1 className="text-2xl font-bold tracking-tight">Applications</h1>
        <p style={{ color: "var(--muted-foreground)" }}>
          All tracked SaaS applications across the organization.
        </p>
      </div>

      {/* Applications data table */}
      <DataTable
        columns={columns}
        data={applications}
        storageKey="applications-table"
        searchKey="name"
        searchPlaceholder="Search applications..."
        onRowClick={(app) => router.push(`/applications/${app.id}`)}
      />
    </div>
  );
}
