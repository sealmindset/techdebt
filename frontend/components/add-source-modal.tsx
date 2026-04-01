"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { apiGet, apiPost } from "@/lib/api";
import type {
  CatalogCategory,
  CatalogItem,
  DataSource,
  TestConnectionResponse,
} from "@/lib/types";
import {
  X,
  Search,
  ChevronRight,
  ChevronLeft,
  CheckCircle,
  XCircle,
  Loader2,
  Zap,
  Star,
  Key,
  Shield,
  User,
  Globe,
  Lock,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type Step = "catalog" | "configure";
type AuthMethod = "api_key" | "oauth2_client_credentials" | "basic_auth";

interface AuthConfig {
  api_key?: string;
  header_name?: string;
  prefix?: string;
  client_id?: string;
  client_secret?: string;
  token_url?: string;
  username?: string;
  password?: string;
}

interface Props {
  onClose: () => void;
  onCreated: (source: DataSource) => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const AUTH_METHOD_OPTIONS: { value: AuthMethod; label: string; icon: typeof Key }[] = [
  { value: "api_key", label: "API Key", icon: Key },
  { value: "oauth2_client_credentials", label: "OAuth 2.0", icon: Shield },
  { value: "basic_auth", label: "Basic Auth", icon: User },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function AddSourceModal({ onClose, onCreated }: Props) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const [step, setStep] = useState<Step>("catalog");
  const [catalog, setCatalog] = useState<CatalogCategory[]>([]);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedItem, setSelectedItem] = useState<CatalogItem | null>(null);

  // Config form state
  const [name, setName] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [authMethod, setAuthMethod] = useState<AuthMethod | "">("");
  const [authConfig, setAuthConfig] = useState<AuthConfig>({});
  const [isPrimary, setIsPrimary] = useState(false);

  // Action state
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<TestConnectionResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load catalog
  useEffect(() => {
    (async () => {
      try {
        const data = await apiGet<CatalogCategory[]>("/data-sources/catalog");
        setCatalog(data);
      } catch {
        setCatalog([]);
      } finally {
        setLoadingCatalog(false);
      }
    })();
  }, []);

  // Close on escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  useEffect(() => {
    dialogRef.current?.focus();
  }, []);

  // Filter catalog
  const filteredCatalog = catalog
    .map((cat) => ({
      ...cat,
      items: cat.items.filter(
        (item) =>
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.vendor.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.description.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter((cat) => cat.items.length > 0);

  // Select catalog item -> advance to config
  const handleSelectItem = useCallback((item: CatalogItem) => {
    setSelectedItem(item);
    setName(item.name);
    setBaseUrl(item.default_base_url || "");
    setAuthMethod("");
    setAuthConfig({});
    setIsPrimary(false);
    setTestResult(null);
    setError(null);
    setStep("configure");
  }, []);

  const updateAuthField = (key: string, value: string) => {
    setAuthConfig((prev) => ({ ...prev, [key]: value }));
  };

  // Test connection (creates source first, then tests -- or test the URL directly)
  const handleTestConnection = async () => {
    if (!baseUrl) return;
    setTesting(true);
    setTestResult(null);
    try {
      // Create a temporary test by hitting the health endpoint directly
      const resp = await fetch(`/api/data-sources/test-url`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ base_url: baseUrl }),
      });
      if (resp.ok) {
        const result = await resp.json();
        setTestResult(result);
      } else {
        // Fallback: test via the backend proxy
        setTestResult({ success: false, message: "Could not reach the endpoint.", latency_ms: null });
      }
    } catch {
      setTestResult({ success: false, message: "Connection test failed.", latency_ms: null });
    } finally {
      setTesting(false);
    }
  };

  // Save
  const handleSave = async () => {
    if (!selectedItem || !name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const source = await apiPost<DataSource>("/data-sources", {
        name: name.trim(),
        source_type: selectedItem.source_type,
        base_url: baseUrl.trim() || null,
        auth_method: authMethod || null,
        auth_config: authMethod ? authConfig : null,
        sync_schedule: "manual",
        sync_enabled: false,
        is_primary: isPrimary,
      });
      onCreated(source);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create data source";
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Render: Catalog Step
  // ---------------------------------------------------------------------------
  const renderCatalog = () => (
    <>
      {/* Search */}
      <div className="border-b p-4" style={{ borderColor: "var(--border)" }}>
        <div
          className="flex items-center gap-2 rounded-lg border px-3 py-2"
          style={{ borderColor: "var(--border)", backgroundColor: "var(--background)" }}
        >
          <Search className="h-4 w-4 shrink-0" style={{ color: "var(--muted-foreground)" }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search integrations..."
            className="w-full bg-transparent text-sm outline-none"
            style={{ color: "var(--foreground)" }}
            autoFocus
          />
        </div>
      </div>

      {/* Catalog grid */}
      <div className="overflow-y-auto p-4" style={{ maxHeight: "60vh" }}>
        {loadingCatalog ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin" style={{ color: "var(--muted-foreground)" }} />
          </div>
        ) : filteredCatalog.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
              {searchQuery ? "No integrations match your search." : "No integrations available."}
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {filteredCatalog.map((cat) => (
              <div key={cat.name}>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
                  {cat.name}
                </h3>
                <p className="mb-3 text-xs" style={{ color: "var(--muted-foreground)" }}>
                  {cat.description}
                </p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {cat.items.map((item) => (
                    <button
                      key={item.key}
                      onClick={() => handleSelectItem(item)}
                      className="flex items-center gap-3 rounded-lg border p-3 text-left transition-all hover:shadow-sm"
                      style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
                    >
                      <div
                        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-sm font-bold"
                        style={{
                          backgroundColor: "color-mix(in oklch, var(--primary) 12%, transparent)",
                          color: "var(--primary)",
                        }}
                      >
                        {item.logo_letter}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold truncate">{item.name}</p>
                        <p className="text-xs truncate" style={{ color: "var(--muted-foreground)" }}>
                          {item.vendor}
                        </p>
                      </div>
                      <ChevronRight className="h-4 w-4 shrink-0" style={{ color: "var(--muted-foreground)" }} />
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );

  // ---------------------------------------------------------------------------
  // Render: Configure Step
  // ---------------------------------------------------------------------------
  const renderConfigure = () => (
    <>
      {/* Back button + selected source header */}
      <div className="border-b p-4" style={{ borderColor: "var(--border)" }}>
        <button
          onClick={() => setStep("catalog")}
          className="mb-3 flex items-center gap-1 text-sm font-medium transition-colors"
          style={{ color: "var(--muted-foreground)" }}
        >
          <ChevronLeft className="h-4 w-4" /> Back to catalog
        </button>
        {selectedItem && (
          <div className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 items-center justify-center rounded-lg text-sm font-bold"
              style={{
                backgroundColor: "color-mix(in oklch, var(--primary) 12%, transparent)",
                color: "var(--primary)",
              }}
            >
              {selectedItem.logo_letter}
            </div>
            <div>
              <p className="text-sm font-semibold">{selectedItem.name}</p>
              <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                {selectedItem.category}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Config form */}
      <div className="space-y-5 overflow-y-auto p-4" style={{ maxHeight: "55vh" }}>
        {/* Name */}
        <div>
          <label className="block text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>
            Display Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2 text-sm outline-none"
            style={{
              backgroundColor: "var(--background)",
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
          />
        </div>

        {/* Connection */}
        <section>
          <h4 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
            <Globe className="h-3.5 w-3.5" /> Connection
          </h4>
          <div className="mt-2">
            <label className="block text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>
              Base URL
            </label>
            <input
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder={selectedItem?.default_base_url || "https://api.example.com"}
              className="mt-1 w-full rounded-md border px-3 py-2 text-sm font-mono outline-none"
              style={{
                backgroundColor: "var(--background)",
                borderColor: "var(--border)",
                color: "var(--foreground)",
              }}
            />
          </div>
          <div className="mt-2 flex items-center gap-3">
            <button
              onClick={handleTestConnection}
              disabled={testing || !baseUrl.trim()}
              className="inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              {testing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5" />}
              Test Connection
            </button>
            {testResult && (
              <span className="flex items-center gap-1 text-xs" style={{ color: testResult.success ? "var(--success, var(--primary))" : "var(--destructive)" }}>
                {testResult.success ? <CheckCircle className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
                {testResult.message}
              </span>
            )}
          </div>
        </section>

        {/* Authentication */}
        <section>
          <h4 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
            <Lock className="h-3.5 w-3.5" /> Authentication
          </h4>
          <div className="mt-2 grid gap-2 sm:grid-cols-3">
            {AUTH_METHOD_OPTIONS.map(({ value, label, icon: Icon }) => {
              const selected = authMethod === value;
              return (
                <button
                  key={value}
                  onClick={() => {
                    setAuthMethod(value);
                    setAuthConfig({});
                  }}
                  className="flex flex-col items-center gap-1 rounded-lg border p-2.5 text-center text-xs font-medium transition-all"
                  style={{
                    borderColor: selected ? "var(--primary)" : "var(--border)",
                    backgroundColor: selected ? "color-mix(in oklch, var(--primary) 8%, transparent)" : "transparent",
                    color: selected ? "var(--primary)" : "var(--muted-foreground)",
                  }}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              );
            })}
          </div>

          {authMethod === "api_key" && (
            <div className="mt-2 space-y-2 rounded-lg border p-3" style={{ borderColor: "var(--border)" }}>
              <FieldInput label="API Key" type="password" value={authConfig.api_key || ""} onChange={(v) => updateAuthField("api_key", v)} />
              <div className="grid gap-2 sm:grid-cols-2">
                <FieldInput label="Header Name" value={authConfig.header_name || "Authorization"} onChange={(v) => updateAuthField("header_name", v)} />
                <FieldInput label="Prefix" value={authConfig.prefix || "Bearer"} onChange={(v) => updateAuthField("prefix", v)} />
              </div>
            </div>
          )}

          {authMethod === "oauth2_client_credentials" && (
            <div className="mt-2 space-y-2 rounded-lg border p-3" style={{ borderColor: "var(--border)" }}>
              <FieldInput label="Client ID" value={authConfig.client_id || ""} onChange={(v) => updateAuthField("client_id", v)} />
              <FieldInput label="Client Secret" type="password" value={authConfig.client_secret || ""} onChange={(v) => updateAuthField("client_secret", v)} />
              <FieldInput label="Token URL" value={authConfig.token_url || ""} onChange={(v) => updateAuthField("token_url", v)} placeholder="https://login.example.com/oauth2/token" />
            </div>
          )}

          {authMethod === "basic_auth" && (
            <div className="mt-2 space-y-2 rounded-lg border p-3" style={{ borderColor: "var(--border)" }}>
              <FieldInput label="Username" value={authConfig.username || ""} onChange={(v) => updateAuthField("username", v)} />
              <FieldInput label="Password" type="password" value={authConfig.password || ""} onChange={(v) => updateAuthField("password", v)} />
            </div>
          )}
        </section>

        {/* Primary source toggle */}
        <section>
          <div className="flex items-center justify-between rounded-lg border p-3" style={{ borderColor: "var(--border)" }}>
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4" style={{ color: isPrimary ? "var(--primary)" : "var(--muted-foreground)" }} />
              <div>
                <p className="text-sm font-medium">Set as Primary Source</p>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                  Primary sources are authoritative for their data fields
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsPrimary(!isPrimary)}
              className="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors"
              style={{ backgroundColor: isPrimary ? "var(--primary)" : "var(--muted)" }}
              role="switch"
              aria-checked={isPrimary}
            >
              <span
                className="pointer-events-none inline-block h-5 w-5 rounded-full shadow-sm transition-transform"
                style={{
                  backgroundColor: "var(--card)",
                  transform: isPrimary ? "translateX(1.25rem)" : "translateX(0)",
                }}
              />
            </button>
          </div>
        </section>

        {/* Error message */}
        {error && (
          <div className="flex items-center gap-2 rounded-lg border p-3" style={{ borderColor: "var(--destructive)", backgroundColor: "color-mix(in oklch, var(--destructive) 8%, transparent)" }}>
            <XCircle className="h-4 w-4 shrink-0" style={{ color: "var(--destructive)" }} />
            <p className="text-sm" style={{ color: "var(--destructive)" }}>{error}</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div
        className="flex items-center justify-end gap-3 border-t p-4"
        style={{ borderColor: "var(--border)" }}
      >
        <button
          onClick={onClose}
          className="rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          style={{ backgroundColor: "var(--muted)", color: "var(--foreground)" }}
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          disabled={saving || !name.trim()}
          className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50"
          style={{ backgroundColor: "var(--primary)" }}
        >
          {saving && <Loader2 className="h-4 w-4 animate-spin" />}
          Add Source
        </button>
      </div>
    </>
  );

  // ---------------------------------------------------------------------------
  // Main render
  // ---------------------------------------------------------------------------
  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        ref={dialogRef}
        tabIndex={-1}
        className="relative mx-4 flex w-full max-w-2xl flex-col rounded-xl border shadow-lg outline-none"
        style={{
          backgroundColor: "var(--card)",
          borderColor: "var(--border)",
          color: "var(--card-foreground)",
          maxHeight: "85vh",
        }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between border-b p-5"
          style={{ borderColor: "var(--border)" }}
        >
          <h2 className="text-lg font-semibold">
            {step === "catalog" ? "Add Data Source" : "Configure Source"}
          </h2>
          <button onClick={onClose} className="rounded-md p-1 transition-colors" style={{ color: "var(--muted-foreground)" }}>
            <X className="h-5 w-5" />
          </button>
        </div>

        {step === "catalog" ? renderCatalog() : renderConfigure()}
      </div>
    </div>,
    document.body
  );
}

// ---------------------------------------------------------------------------
// Sub-component
// ---------------------------------------------------------------------------
function FieldInput({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
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
        className="mt-1 w-full rounded-md border px-3 py-1.5 text-sm outline-none"
        style={{
          backgroundColor: "var(--background)",
          borderColor: "var(--border)",
          color: "var(--foreground)",
        }}
      />
    </div>
  );
}
