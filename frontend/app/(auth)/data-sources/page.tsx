"use client";

import { useEffect, useState, useCallback } from "react";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDateTime, formatRelative } from "@/lib/utils";
import type { DataSource } from "@/lib/types";
import DataSourceConfigModal from "@/components/data-source-config-modal";
import AddSourceModal from "@/components/add-source-modal";
import {
  Database,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
  Plus,
  Star,
} from "lucide-react";

const SOURCE_TYPE_ICONS: Record<string, typeof Database> = {
  workday: Database,
  auditboard: Database,
  entra_id: Database,
  voluntary: Database,
};

const STATUS_CONFIG: Record<
  string,
  { icon: typeof CheckCircle; color: string; label: string }
> = {
  connected: {
    icon: CheckCircle,
    color: "var(--success, var(--primary))",
    label: "Connected",
  },
  disconnected: {
    icon: XCircle,
    color: "var(--muted-foreground)",
    label: "Disconnected",
  },
  error: {
    icon: AlertCircle,
    color: "var(--destructive)",
    label: "Error",
  },
  syncing: {
    icon: RefreshCw,
    color: "var(--primary)",
    label: "Syncing",
  },
};

export default function DataSourcesPage() {
  const { hasPermission } = useAuth();
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const canCreate = hasPermission("data_sources", "create");

  const fetchDataSources = useCallback(async () => {
    try {
      const data = await apiGet<DataSource[]>("/data-sources");
      setDataSources(data);
    } catch (err) {
      console.error("Failed to load data sources:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDataSources();
  }, [fetchDataSources]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div
          className="h-8 w-48 animate-pulse rounded"
          style={{ backgroundColor: "var(--muted)" }}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-40 animate-pulse rounded-xl border"
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
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Data Sources</h1>
          <p style={{ color: "var(--muted-foreground)" }}>
            Connected data sources feeding application intelligence.
          </p>
        </div>
        {canCreate && (
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors"
            style={{ backgroundColor: "var(--primary)" }}
          >
            <Plus className="h-4 w-4" />
            Add Source
          </button>
        )}
      </div>

      {/* Data source cards */}
      <div className="grid gap-4 sm:grid-cols-2">
        {dataSources.map((source) => {
          const statusConfig =
            STATUS_CONFIG[source.status] || STATUS_CONFIG.disconnected;
          const StatusIcon = statusConfig.icon;

          return (
            <div
              key={source.id}
              className="cursor-pointer rounded-xl border transition-shadow hover:shadow-md"
              onClick={() => setSelectedSource(source)}
              style={{
                backgroundColor: "var(--card)",
                borderColor: "var(--border)",
                color: "var(--card-foreground)",
              }}
            >
              {/* Card header */}
              <div className="flex items-start justify-between p-5">
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-10 w-10 items-center justify-center rounded-lg"
                    style={{
                      backgroundColor:
                        "color-mix(in oklch, var(--primary) 12%, transparent)",
                      color: "var(--primary)",
                    }}
                  >
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{source.name}</h3>
                    <p
                      className="text-sm capitalize"
                      style={{ color: "var(--muted-foreground)" }}
                    >
                      {source.source_type.replace(/_/g, " ")}
                    </p>
                  </div>
                </div>

                {/* Status badge + primary indicator */}
                <div className="flex items-center gap-2">
                  {source.is_primary && (
                    <span
                      className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
                      style={{
                        backgroundColor: "color-mix(in oklch, var(--primary) 12%, transparent)",
                        color: "var(--primary)",
                      }}
                    >
                      <Star className="h-3 w-3" />
                      Primary
                    </span>
                  )}
                  <div className="flex items-center gap-1.5">
                    <StatusIcon
                      className={`h-4 w-4 ${source.status === "syncing" ? "animate-spin" : ""}`}
                      style={{ color: statusConfig.color }}
                    />
                    <span
                      className="text-sm font-medium"
                      style={{ color: statusConfig.color }}
                    >
                      {statusConfig.label}
                    </span>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div
                className="grid grid-cols-2 gap-4 border-t px-5 py-4"
                style={{ borderColor: "var(--border)" }}
              >
                <div>
                  <p
                    className="text-xs font-medium"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    Records Synced
                  </p>
                  <p className="mt-1 text-lg font-bold">
                    {source.records_synced.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p
                    className="text-xs font-medium"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    Last Sync
                  </p>
                  <p className="mt-1 text-sm font-medium">
                    {source.last_sync_at
                      ? formatRelative(source.last_sync_at)
                      : "Never"}
                  </p>
                </div>
              </div>

              {/* Error message */}
              {source.error_message && (
                <div
                  className="border-t px-5 py-3"
                  style={{ borderColor: "var(--border)" }}
                >
                  <div className="flex items-start gap-2">
                    <AlertCircle
                      className="mt-0.5 h-3.5 w-3.5 shrink-0"
                      style={{ color: "var(--destructive)" }}
                    />
                    <p
                      className="text-xs"
                      style={{ color: "var(--destructive)" }}
                    >
                      {source.error_message}
                    </p>
                  </div>
                </div>
              )}

              {/* Footer */}
              <div
                className="border-t px-5 py-2"
                style={{ borderColor: "var(--border)" }}
              >
                <div className="flex items-center gap-1">
                  <Clock
                    className="h-3 w-3"
                    style={{ color: "var(--muted-foreground)" }}
                  />
                  <span
                    className="text-xs"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    {source.last_sync_at
                      ? `Last synced ${formatDateTime(source.last_sync_at)}`
                      : "No sync recorded"}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {dataSources.length === 0 && (
        <div
          className="rounded-xl border p-12 text-center"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
          }}
        >
          <Database
            className="mx-auto h-12 w-12"
            style={{ color: "var(--muted-foreground)" }}
          />
          <h3 className="mt-4 text-lg font-semibold">No data sources</h3>
          <p
            className="mt-2 text-sm"
            style={{ color: "var(--muted-foreground)" }}
          >
            Data sources will appear here once configured.
          </p>
        </div>
      )}

      {/* Configuration modal */}
      {selectedSource && (
        <DataSourceConfigModal
          source={selectedSource}
          onClose={() => setSelectedSource(null)}
          onSaved={() => {
            setSelectedSource(null);
            fetchDataSources();
          }}
        />
      )}

      {/* Add Source modal */}
      {showAddModal && (
        <AddSourceModal
          onClose={() => setShowAddModal(false)}
          onCreated={() => {
            setShowAddModal(false);
            fetchDataSources();
          }}
        />
      )}
    </div>
  );
}
