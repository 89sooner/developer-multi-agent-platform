export type ConfidenceLevel = "low" | "medium" | "high";
export type RunStatus = "queued" | "running" | "completed" | "failed" | "canceled";
export type ConnectorHealthStatus = "ok" | "degraded" | "unconfigured";

export interface Evidence {
  source_type: string;
  source_id?: string | null;
  locator: string;
  snippet?: string | null;
  timestamp?: string | null;
  confidence: ConfidenceLevel;
}

export interface BaseWorkflowResponse {
  run_id: string;
  status: RunStatus;
  trace_id: string;
  request_type: string;
  primary_intent: string;
  secondary_intents: string[];
  selected_agents: string[];
  model_version: string;
  skill_versions: Record<string, string>;
  prompt_versions: Record<string, string>;
  warnings: string[];
  confidence: ConfidenceLevel;
}

export interface PlanResponse extends BaseWorkflowResponse {
  summary: string;
  impacted_areas: string[];
  implementation_plan: string[];
  tests: string[];
  risks: string[];
  open_questions: string[];
  evidence: Evidence[];
}

export interface ReviewFinding {
  category: string;
  severity: ConfidenceLevel;
  message: string;
  evidence: Evidence[];
}

export interface ReviewResponse extends BaseWorkflowResponse {
  summary: string;
  review_findings: ReviewFinding[];
  missing_tests: string[];
  risks: string[];
  readiness_verdict: "ready" | "needs_changes" | "blocked";
  evidence: Evidence[];
}

export interface TestPlanResponse extends BaseWorkflowResponse {
  unit_tests: string[];
  integration_tests: string[];
  regression_targets: string[];
  edge_cases: string[];
  execution_order: string[];
}

export interface RunDetailResponse {
  run_id: string;
  status: string;
  created_at: string;
  completed_at?: string | null;
  request_type: string;
  primary_intent: string;
  secondary_intents: string[];
  selected_agents: string[];
  user_id: string;
  repo_scope: string[];
  model_version: string;
  skill_versions: Record<string, string>;
  prompt_versions: Record<string, string>;
  request: Record<string, unknown>;
  result: Record<string, unknown>;
  trace_id: string;
}

export interface TraceStep {
  step_name: string;
  step_order: number;
  status: string;
  started_at: string;
  ended_at: string;
  latency_ms: number;
  tool_calls: number;
  confidence?: ConfidenceLevel | null;
  input_ref?: string | null;
  output_ref?: string | null;
  error_message?: string | null;
}

export interface ToolCallRecord {
  step_name: string;
  tool_name: string;
  status: string;
  started_at: string;
  ended_at: string;
  duration_ms: number;
  input_summary: string;
  output_count: number;
  error_message?: string | null;
}

export interface TraceResponse {
  trace_id: string;
  steps: TraceStep[];
  spans: TraceStep[];
  tool_calls: ToolCallRecord[];
  metadata: Record<string, unknown>;
  exported_at?: string | null;
  error_summary?: string | null;
}

export interface FeedbackResponse {
  feedback_id: string;
  stored: boolean;
}

export interface ConnectorHealth {
  status: ConnectorHealthStatus;
  detail?: string | null;
}

export interface HealthResponse {
  status: "ok" | "degraded";
  version: string;
  connectors: Record<string, ConnectorHealth>;
}

export interface ErrorResponse {
  code: string;
  message: string;
  request_id: string;
  detail?: unknown;
}
