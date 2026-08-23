/**
 * AgentCrashLab — TypeScript type definitions
 * Mirrors backend Pydantic schemas
 */

// --- Agent Types ---

export interface Tool {
  id: string;
  name: string;
  description: string | null;
  parameters_schema: Record<string, unknown> | null;
  permissions: Record<string, unknown> | null;
  is_destructive: boolean;
  requires_confirmation: boolean;
  created_at: string;
}

export interface AgentVersion {
  id: string;
  agent_id: string;
  version: string;
  system_prompt: string;
  model_provider: string;
  model_name: string;
  config: Record<string, unknown> | null;
  tools: Tool[];
  created_at: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string | null;
  versions: AgentVersion[];
  created_at: string;
  updated_at: string;
}

// --- Scenario Types ---

export type ScenarioCategory =
  | 'normal'
  | 'edge_case'
  | 'ambiguous'
  | 'adversarial'
  | 'tool_failure'
  | 'destructive_action'
  | 'long_horizon';

export type Severity = 'low' | 'medium' | 'high' | 'critical';

export interface Scenario {
  id: string;
  category: ScenarioCategory;
  severity: Severity;
  title: string;
  user_input: string;
  objective: string | null;
  expected_behavior: string;
  forbidden_behavior: string | null;
  tools_involved: string[] | null;
  setup_state: Record<string, unknown> | null;
  created_at: string;
}

// --- Test Run Types ---

export type TestRunStatus = 'pending' | 'running' | 'passed' | 'failed' | 'error' | 'timeout';

export interface ExecutionStep {
  id: string;
  step_index: number;
  step_type: 'user_input' | 'agent_message' | 'tool_call' | 'tool_result' | 'system_error';
  content: string | null;
  tool_name: string | null;
  tool_args: Record<string, unknown> | null;
  tool_result: Record<string, unknown> | null;
  latency_ms: number | null;
  error: string | null;
  timestamp: string;
}

export interface TestRun {
  id: string;
  agent_version_id: string;
  scenario_id: string;
  status: TestRunStatus;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  trace: Record<string, unknown> | null;
  metrics: Record<string, unknown> | null;
  created_at: string;
}

export interface TestRunDetail extends TestRun {
  execution_steps: ExecutionStep[];
  failures: Failure[];
}

export interface TestRunCreate {
  agent_id: string;
  agent_version_id?: string;
  scenario_id: string;
  behavior_mode: 'realistic' | 'safe' | 'unsafe';
}

// --- Failure Types ---

export type FailureCategory = 'safety' | 'security' | 'reasoning' | 'tool_usage' | 'resilience';

export interface Failure {
  id: string;
  test_run_id: string;
  category: FailureCategory;
  subcategory: string | null;
  severity: Severity;
  title: string;
  description: string | null;
  expected_behavior: string | null;
  actual_behavior: string | null;
  root_cause: string | null;
  contributing_factors: string[];
  evidence: string[];
  is_reproducible: boolean;
  suggested_fix?: {
    proposed_system_prompt: string;
    explanation: string;
  };
  created_at: string;
}

// --- Health ---

export interface HealthStatus {
  status: string;
  version: string;
  database: string;
}

// --- Dashboard Stats ---

export interface DashboardStats {
  agent: Agent | null;
  totalTests: number;
  passed: number;
  failed: number;
  critical: number;
  reliability: number;
}
