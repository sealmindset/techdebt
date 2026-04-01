"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { apiPost, apiPut } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type {
  DataSource,
  TestConnectionResponse,
  SyncResponse,
} from "@/lib/types";
import {
  X,
  CheckCircle,
  XCircle,
  Loader2,
  Zap,
  RefreshCw,
  Shield,
  Clock,
  Key,
  User,
  Lock,
  Globe,
  Info,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type AuthMethod = "api_key" | "oauth2_client_credentials" | "basic_auth";

interface AuthConfig {
  // api_key
  api_key?: string;
  header_name?: string;
  prefix?: string;
  // oauth2
  client_id?: string;
  client_secret?: string;
  token_url?: string;
  // basic
  username?: string;
  password?: string;
}

type SyncSchedule = "hourly" | "daily" | "weekly" | "manual";

interface Props {
  source: DataSource;
  onClose: () => void;
  onSaved: () => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const AUTH_METHOD_OPTIONS: { value: AuthMethod; label: string; icon: typeof Key }[] = [
  { value: "api_key", label: "API Key / Bearer Token", icon: Key },
  { value: "oauth2_client_credentials", label: "OAuth 2.0 Client Credentials", icon: Shield },
  { value: "basic_auth", label: "Basic Authentication", icon: User },
];

const SYNC_SCHEDULE_OPTIONS: { value: SyncSchedule; label: string; desc: string }[] = [
  { value: "hourly", label: "Hourly", desc: "Every hour" },
  { value: "daily", label: "Daily", desc: "Once per day" },
  { value: "weekly", label: "Weekly", desc: "Once per week" },
  { value: "manual", label: "Manual Only", desc: "On-demand only" },
];

const SOURCE_TYPE_LABELS: Record<string, string> = {
  procurement: "Procurement & Contracts",
  vendor_risk: "Vendor Risk Assessment",
  identity_analytics: "Identity & Access Analytics",
  spend_analytics: "Vendor Spend Analytics",
  manual: "Voluntary Submissions",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function DataSourceConfigModal({ source, onClose, onSaved }: Props) {
  const { hasPermission } = useAuth();
  const canEdit = hasPermission("data_sources", "update");
  const dialogRef = useRef<HTMLDivElement>(null);

  // Form state
  const [authMethod, setAuthMethod] = useState<AuthMethod | "">(
    (source.auth_method as AuthMethod) || ""
  );
  const [authConfig, setAuthConfig] = useState<AuthConfig>(() => {
    const masked = source.auth_config_masked || {};
    return { ...masked } as AuthConfig;
  });
  const [syncSchedule, setSyncSchedule] = useState<SyncSchedule>(
    (source.sync_schedule as SyncSchedule) || "manual"
  );
  const [syncEnabled, setSyncEnabled] = useState(source.sync_enabled);

  // Action state
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<TestConnectionResponse | null>(null);
  const [testing, setTesting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResponse | null>(null);
  const [dirty, setDirty] = useState(false);

  // Close on escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  // Focus trap: focus the dialog on mount
  useEffect(() => {
    dialogRef.current?.focus();
  }, []);

  // Mark dirty on any change
  const markDirty = useCallback(() => setDirty(true), []);

  // ----- Handlers -----
  const handleAuthMethodChange = (method: AuthMethod) => {
    setAuthMethod(method);
    setAuthConfig({});
    markDirty();
  };

  const updateAuthField = (key: string, value: string) => {
    setAuthConfig((prev) => ({ ...prev, [key]: value }));
    markDirty();
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await apiPost<TestConnectionResponse>(
        `/data-sources/${source.id}/test-connection`
      );
      setTestResult(result);
    } catch {
      setTestResult({ success: false, message: "Request failed.", latency_ms: null });
    } finally {
      setTesting(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const result = await apiPost<SyncResponse>(
        `/data-sources/${source.id}/sync`
      );
      setSyncResult(result);
    } catch {
      setSyncResult({ status: "error", records_synced: null, message: "Sync request failed." });
    } finally {
      setSyncing(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiPut(`/data-sources/${source.id}/config`, {
        auth_method: authMethod || null,
        auth_config: authMethod ? authConfig : null,
        sync_schedule: syncSchedule,
        sync_enabled: syncEnabled,
      });
      onSaved();
    } catch {
      // stay open so user can retry
    } finally {
      setSaving(false);
    }
  };

  // ----- Voluntary Submissions: simplified view -----
  if (source.source_type === "manual") {
    return createPortal(
      <div
        className="fixed inset-0 z-50 flex items-center justify-center"
        style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
        onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      >
        <div
          ref={dialogRef}
          tabIndex={-1}
          className="relative mx-4 w-full max-w-lg rounded-xl border shadow-lg outline-none"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--card-foreground)",
          }}
        >
          <div className="flex items-center justify-between border-b p-5" style={{ borderColor: "var(--border)" }}>
            <h2 className="text-lg font-semibold">{source.name}</h2>
            <button onClick={onClose} className="rounded-md p-1 transition-colors" style={{ color: "var(--muted-foreground)" }}>
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="p-6 text-center">
            <div
              className="mx-auto flex h-14 w-14 items-center justify-center rounded-full"
              style={{ backgroundColor: "color-mix(in oklch, var(--primary) 12%, transparent)" }}
            >
              <Info className="h-7 w-7" style={{ color: "var(--primary)" }} />
            </div>
            <h3 className="mt-4 text-base font-semibold">Coming Soon</h3>
            <p className="mt-2 text-sm" style={{ color: "var(--muted-foreground)" }}>
              A built-in submission form will allow department heads and team leads
              to voluntarily report applications used by their teams.
            </p>
            <p className="mt-3 text-sm" style={{ color: "var(--muted-foreground)" }}>
              Until then, submissions can be collected via the <strong>Submissions</strong> page
              or imported from spreadsheets.
            </p>
          </div>
          <div className="border-t p-4 text-right" style={{ borderColor: "var(--border)" }}>
            <button
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
              style={{ backgroundColor: "var(--muted)", color: "var(--foreground)" }}
            >
              Close
            </button>
          </div>
        </div>
      </div>,
      document.body
    );
  }

  // ----- Full config modal -----
  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        ref={dialogRef}
        tabIndex={-1}
        className="relative mx-4 w-full max-w-2xl rounded-xl border shadow-lg outline-none"
        style={{
          backgroundColor: "var(--card)",
          borderColor: "var(--border)",
          color: "var(--card-foreground)",
          maxHeight: "85vh",
          overflowY: "auto",
        }}
      >
        {/* Header */}
        <div
          className="sticky top-0 z-10 flex items-center justify-between border-b p-5"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <div>
            <h2 className="text-lg font-semibold">{source.name}</h2>
            <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
              {SOURCE_TYPE_LABELS[source.source_type] || source.source_type}
            </p>
          </div>
          <button onClick={onClose} className="rounded-md p-1 transition-colors" style={{ color: "var(--muted-foreground)" }}>
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-6 p-5">
          {/* ---- Section 1: Connection Details ---- */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
              <Globe className="h-4 w-4" /> Connection
            </h3>
            <div className="mt-3 space-y-3">
              <div className="flex items-center justify-between rounded-lg border p-3" style={{ borderColor: "var(--border)" }}>
                <div>
                  <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>Base URL</p>
                  <p className="mt-0.5 text-sm font-mono">{source.base_url || "Not configured"}</p>
                </div>
                <StatusBadge status={source.status} />
              </div>

              {/* Test Connection */}
              <div className="flex items-center gap-3">
                <button
                  onClick={handleTestConnection}
                  disabled={testing || !canEdit}
                  className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors disabled:opacity-50"
                  style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                >
                  {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                  Test Connection
                </button>
                {testResult && (
                  <span className="flex items-center gap-1.5 text-sm" style={{ color: testResult.success ? "var(--success, var(--primary))" : "var(--destructive)" }}>
                    {testResult.success ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                    {testResult.message}
                    {testResult.latency_ms != null && ` (${testResult.latency_ms}ms)`}
                  </span>
                )}
              </div>
            </div>
          </section>

          {/* ---- Section 2: Authentication ---- */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
              <Lock className="h-4 w-4" /> Authentication
            </h3>
            <div className="mt-3 space-y-3">
              {/* Auth method selector */}
              <div className="grid gap-2 sm:grid-cols-3">
                {AUTH_METHOD_OPTIONS.map(({ value, label, icon: Icon }) => {
                  const selected = authMethod === value;
                  return (
                    <button
                      key={value}
                      onClick={() => canEdit && handleAuthMethodChange(value)}
                      disabled={!canEdit}
                      className="flex flex-col items-center gap-1.5 rounded-lg border p-3 text-center text-xs font-medium transition-all disabled:opacity-50"
                      style={{
                        borderColor: selected ? "var(--primary)" : "var(--border)",
                        backgroundColor: selected ? "color-mix(in oklch, var(--primary) 8%, transparent)" : "transparent",
                        color: selected ? "var(--primary)" : "var(--muted-foreground)",
                      }}
                    >
                      <Icon className="h-5 w-5" />
                      {label}
                    </button>
                  );
                })}
              </div>

              {/* Dynamic auth fields */}
              {authMethod === "api_key" && (
                <div className="space-y-3 rounded-lg border p-4" style={{ borderColor: "var(--border)" }}>
                  <InputField label="API Key" type="password" value={authConfig.api_key || ""} onChange={(v) => updateAuthField("api_key", v)} disabled={!canEdit} />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <InputField label="Header Name" value={authConfig.header_name || "Authorization"} onChange={(v) => updateAuthField("header_name", v)} disabled={!canEdit} />
                    <InputField label="Prefix" value={authConfig.prefix || "Bearer"} onChange={(v) => updateAuthField("prefix", v)} disabled={!canEdit} />
                  </div>
                </div>
              )}

              {authMethod === "oauth2_client_credentials" && (
                <div className="space-y-3 rounded-lg border p-4" style={{ borderColor: "var(--border)" }}>
                  <InputField label="Client ID" value={authConfig.client_id || ""} onChange={(v) => updateAuthField("client_id", v)} disabled={!canEdit} />
                  <InputField label="Client Secret" type="password" value={authConfig.client_secret || ""} onChange={(v) => updateAuthField("client_secret", v)} disabled={!canEdit} />
                  <InputField label="Token URL" value={authConfig.token_url || ""} onChange={(v) => updateAuthField("token_url", v)} placeholder="https://login.microsoftonline.com/.../oauth2/v2.0/token" disabled={!canEdit} />
                </div>
              )}

              {authMethod === "basic_auth" && (
                <div className="space-y-3 rounded-lg border p-4" style={{ borderColor: "var(--border)" }}>
                  <InputField label="Username" value={authConfig.username || ""} onChange={(v) => updateAuthField("username", v)} disabled={!canEdit} />
                  <InputField label="Password" type="password" value={authConfig.password || ""} onChange={(v) => updateAuthField("password", v)} disabled={!canEdit} />
                </div>
              )}

              {!authMethod && (
                <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                  Select an authentication method to configure credentials.
                </p>
              )}
            </div>
          </section>

          {/* ---- Section 3: Sync Schedule ---- */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
              <Clock className="h-4 w-4" /> Sync Schedule
            </h3>
            <div className="mt-3 space-y-4">
              {/* Schedule options */}
              <div className="grid gap-2 sm:grid-cols-4">
                {SYNC_SCHEDULE_OPTIONS.map(({ value, label, desc }) => {
                  const selected = syncSchedule === value;
                  return (
                    <button
                      key={value}
                      onClick={() => { if (canEdit) { setSyncSchedule(value); markDirty(); } }}
                      disabled={!canEdit}
                      className="rounded-lg border p-3 text-left transition-all disabled:opacity-50"
                      style={{
                        borderColor: selected ? "var(--primary)" : "var(--border)",
                        backgroundColor: selected ? "color-mix(in oklch, var(--primary) 8%, transparent)" : "transparent",
                      }}
                    >
                      <p className="text-sm font-medium" style={{ color: selected ? "var(--primary)" : "var(--foreground)" }}>{label}</p>
                      <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>{desc}</p>
                    </button>
                  );
                })}
              </div>

              {/* Auto-sync toggle */}
              <div className="flex items-center justify-between rounded-lg border p-3" style={{ borderColor: "var(--border)" }}>
                <div>
                  <p className="text-sm font-medium">Enable Automatic Sync</p>
                  <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                    Automatically pull data on the selected schedule
                  </p>
                </div>
                <button
                  onClick={() => { if (canEdit) { setSyncEnabled(!syncEnabled); markDirty(); } }}
                  disabled={!canEdit}
                  className="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors disabled:opacity-50"
                  style={{ backgroundColor: syncEnabled ? "var(--primary)" : "var(--muted)" }}
                  role="switch"
                  aria-checked={syncEnabled}
                >
                  <span
                    className="pointer-events-none inline-block h-5 w-5 rounded-full shadow-sm transition-transform"
                    style={{
                      backgroundColor: "var(--card)",
                      transform: syncEnabled ? "translateX(1.25rem)" : "translateX(0)",
                    }}
                  />
                </button>
              </div>

              {/* Sync now + last sync info */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleSync}
                    disabled={syncing || !canEdit}
                    className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50"
                    style={{ backgroundColor: "var(--primary)" }}
                  >
                    {syncing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    Sync Now
                  </button>
                  {syncResult && (
                    <span
                      className="flex items-center gap-1.5 text-sm"
                      style={{ color: syncResult.status === "completed" ? "var(--success, var(--primary))" : "var(--destructive)" }}
                    >
                      {syncResult.status === "completed" ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                      {syncResult.message}
                    </span>
                  )}
                </div>
                <div className="text-right text-xs" style={{ color: "var(--muted-foreground)" }}>
                  <p>{source.records_synced.toLocaleString()} records</p>
                  <p>{source.last_sync_at ? `Last: ${new Date(source.last_sync_at).toLocaleString()}` : "Never synced"}</p>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div
          className="sticky bottom-0 flex items-center justify-end gap-3 border-t p-4"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <button
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
            style={{ backgroundColor: "var(--muted)", color: "var(--foreground)" }}
          >
            Cancel
          </button>
          {canEdit && (
            <button
              onClick={handleSave}
              disabled={saving || !dirty}
              className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50"
              style={{ backgroundColor: "var(--primary)" }}
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              Save Configuration
            </button>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { color: string; label: string }> = {
    connected: { color: "var(--success, var(--primary))", label: "Connected" },
    disconnected: { color: "var(--muted-foreground)", label: "Disconnected" },
    error: { color: "var(--destructive)", label: "Error" },
    syncing: { color: "var(--primary)", label: "Syncing" },
  };
  const c = config[status] || config.disconnected;
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium" style={{ color: c.color }}>
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: c.color }} />
      {c.label}
    </span>
  );
}

function InputField({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  disabled?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="mt-1 w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors disabled:opacity-50"
        style={{
          backgroundColor: "var(--background)",
          borderColor: "var(--border)",
          color: "var(--foreground)",
        }}
      />
    </div>
  );
}
