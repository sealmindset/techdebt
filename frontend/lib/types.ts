// AuthMe matches JWT payload EXACTLY -- flat, no .user wrapper
export interface AuthMe {
  sub: string;
  email: string;
  name: string;
  role_id: string;
  role_name: string;
  permissions: string[];
}

export interface User {
  id: string;
  oidc_subject: string;
  email: string;
  display_name: string;
  is_active: boolean;
  role_id: string;
  role_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface Permission {
  id: string;
  resource: string;
  action: string;
  description: string | null;
}

export interface RoleWithPermissions extends Role {
  permissions: Permission[];
}

// ---------------------------------------------------------------------------
// AI Prompt Management
// ---------------------------------------------------------------------------

export interface ManagedPrompt {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  category: string;
  provider: string | null;
  model: string | null;
  current_version: number;
  is_active: boolean;
  is_locked: boolean;
  locked_by: string | null;
  locked_reason: string | null;
  source_file: string | null;
  created_by: string;
  updated_by: string | null;
  created_at: string;
  updated_at: string;
  tags: string[];
  primary_usage_location: string | null;
  version_count?: number;
  usage_count?: number;
}

export interface ManagedPromptListItem {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  category: string;
  provider: string | null;
  model: string | null;
  current_version: number;
  is_active: boolean;
  is_locked: boolean;
  updated_at: string;
  tags: string[];
  primary_usage_location: string | null;
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  version: number;
  content: string;
  system_message: string | null;
  parameters: Record<string, unknown> | null;
  model: string | null;
  change_summary: string | null;
  created_by: string;
  created_at: string;
}

export interface PromptVersionDiff {
  version_a: number;
  version_b: number;
  content_diff: string | null;
  system_message_diff: string | null;
  parameters_a: Record<string, unknown> | null;
  parameters_b: Record<string, unknown> | null;
}

export interface PromptUsage {
  id: string;
  prompt_id: string;
  usage_type: string;
  location: string;
  description: string | null;
  is_primary: boolean;
  call_count: number;
  avg_latency_ms: number | null;
  avg_tokens_in: number | null;
  avg_tokens_out: number | null;
  error_count: number;
  created_at: string;
  updated_at: string;
}

export interface PromptTestCase {
  id: string;
  prompt_id: string;
  name: string;
  input_data: Record<string, unknown> | null;
  expected_output: string | null;
  notes: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface PromptTestRun {
  output: string;
  tokens_in: number | null;
  tokens_out: number | null;
  latency_ms: number | null;
  success: boolean;
  error: string | null;
}

export interface PromptAuditLogEntry {
  id: string;
  action: string;
  prompt_id: string | null;
  prompt_slug: string | null;
  version: number | null;
  user_id: string | null;
  user_email: string | null;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  created_at: string;
}

export interface PromptStats {
  total: number;
  active: number;
  versions_count: number;
  categories_count: number;
}

export interface PromptTag {
  tag: string;
  count: number;
}

// ---------------------------------------------------------------------------
// Domain Types: TechDebt SaaS Rationalization
// ---------------------------------------------------------------------------

export interface Application {
  id: string;
  name: string;
  vendor: string;
  category: string;
  app_type: string;
  status: string;
  annual_cost: number;
  cost_per_license: number;
  total_licenses: number;
  active_users: number;
  adoption_rate: number;
  contract_start: string;
  contract_end: string;
  risk_score: number;
  compliance_status: string;
  department: string;
  description: string | null;
  owner_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Recommendation {
  id: string;
  application_id: string;
  application_name: string | null;
  recommendation_type: "keep" | "cut" | "replace" | "consolidate";
  confidence_score: number;
  reasoning: string;
  cost_savings_estimate: number;
  alternative_app: string | null;
  evidence: string | null;
  status: string;
  reviewed_by: string | null;
  created_at: string;
  updated_at: string;
  application?: Application;
}

export interface Decision {
  id: string;
  application_id: string;
  application_name: string | null;
  decision_type: string;
  justification: string;
  submitted_by: string;
  submitter_name: string | null;
  reviewer_id: string | null;
  status: "pending_review" | "approved" | "rejected" | "implemented";
  review_notes: string | null;
  cost_impact: number;
  created_at: string;
  updated_at: string;
  application?: Application;
}

export interface DataSource {
  id: string;
  name: string;
  source_type: string;
  base_url: string | null;
  status: string;
  auth_method: string | null;
  auth_config_masked: Record<string, string> | null;
  sync_schedule: string;
  sync_enabled: boolean;
  is_primary: boolean;
  last_sync_at: string | null;
  records_synced: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface TestConnectionResponse {
  success: boolean;
  message: string;
  latency_ms: number | null;
}

export interface SyncResponse {
  status: string;
  records_synced: number | null;
  message: string;
}

export interface CatalogItem {
  key: string;
  name: string;
  vendor: string;
  source_type: string;
  category: string;
  description: string;
  default_base_url: string | null;
  logo_letter: string;
}

export interface CatalogCategory {
  name: string;
  description: string;
  items: CatalogItem[];
}

export interface Submission {
  id: string;
  app_name: string;
  vendor: string;
  department: string;
  submitted_by: string;
  usage_frequency: string;
  user_count: number;
  estimated_cost: number;
  business_justification: string;
  status: string;
  matched_application_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_apps: number;
  total_spend: number;
  avg_adoption_rate: number;
  total_potential_savings: number;
  apps_by_status: Record<string, number>;
  apps_by_category: Record<string, number>;
  recommendations_summary: Record<string, number>;
  top_savings_opportunities: Array<{
    id: string;
    name: string;
    vendor: string;
    annual_cost: number;
    savings_estimate: number;
    recommendation_type: string;
  }>;
  recent_decisions: Array<{
    id: string;
    application_name: string;
    decision_type: string;
    status: string;
    submitted_by: string;
    created_at: string;
  }>;
}
