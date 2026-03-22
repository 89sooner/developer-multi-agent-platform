import type { HealthResponse } from "./contracts/responses";
import { fetchJson } from "./http";

export function getHealth() {
  return fetchJson<HealthResponse>("/health");
}
