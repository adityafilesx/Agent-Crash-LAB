/**
 * AgentCrashLab — API Client
 * Centralized API communication with the backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}/api${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body);
  }

  return response.json();
}

// --- Health ---

export async function getHealth() {
  return request<{ status: string; version: string; database: string }>('/health');
}

// --- Agents ---

export async function getAgents() {
  return request<import('../types').Agent[]>('/agents');
}

export async function getAgent(id: string) {
  return request<import('../types').Agent>(`/agents/${id}`);
}

export async function cloneAgentVersion(agentId: string, payload: { original_version_id: string, new_version_name: string, new_system_prompt: string }) {
  return request<any>(`/agents/${agentId}/versions/clone`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --- Scenarios ---

export async function getScenarios(category?: string) {
  const params = category ? `?category=${category}` : '';
  return request<import('../types').Scenario[]>(`/scenarios${params}`);
}

export async function getScenario(id: string) {
  return request<import('../types').Scenario>(`/scenarios/${id}`);
}

export async function generateScenarios(payload: { agent_version_id: string }) {
  return request<import('../types').Scenario[]>('/scenarios/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --- Test Runs ---

export async function getTestRuns() {
  return request<import('../types').TestRun[]>('/test-runs');
}

export async function getTestRun(id: string) {
  return request<import('../types').TestRunDetail>(`/test-runs/${id}`);
}

export async function createTestRun(payload: import('../types').TestRunCreate) {
  return request<import('../types').TestRunDetail>('/test-runs', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export { ApiError };
