export type Strategy = { id: string; name: string; version: string; status: string; description: string; parameters: Record<string, {default: number}>; risk_notice: string };
export type Run = { id: string; status: string; created_at: string; error?: string; git_commit?: string; data_hash?: string; request: Record<string, unknown> };
export type Result = { metrics: Record<string, number>; equity: Array<{date: string; equity: number; drawdown: number}>; trades: Array<Record<string, string | number>>; provenance: Record<string, string> };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!response.ok) throw new Error((await response.text()) || `HTTP ${response.status}`);
  return response.json();
}

export const api = {
  strategies: () => request<Strategy[]>("/api/strategies"),
  snapshots: () => request<Array<Record<string, unknown>>>("/api/data-snapshots"),
  runs: () => request<Run[]>("/api/backtests"),
  result: (id: string) => request<Result>(`/api/backtests/${id}/results`),
  createRun: (payload: Record<string, unknown>) => request<{run_id: string}>("/api/backtests", { method: "POST", body: JSON.stringify(payload) }),
  compare: (run_ids: string[]) => request<{runs: Array<{run_id: string; metrics: Record<string, number>; equity: Result["equity"]}>}>("/api/comparisons", { method: "POST", body: JSON.stringify({run_ids}) }),
  experiments: () => request<Array<Record<string, unknown>>>("/api/experiments"),
  createExperiment: (payload: Record<string, unknown>) => request("/api/experiments", { method: "POST", body: JSON.stringify(payload) }),
  reload: () => request("/api/strategies/reload", { method: "POST" })
};

