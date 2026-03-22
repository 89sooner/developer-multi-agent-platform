import type { ErrorResponse } from "./contracts/responses";

export interface ClientError {
  http_status: number;
  code: string;
  message: string;
  request_id?: string;
  detail?: unknown;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export async function parseClientError(response: Response): Promise<ClientError> {
  let payload: ErrorResponse | undefined;

  try {
    const candidate = await response.json();
    if (isObject(candidate)) {
      payload = candidate as unknown as ErrorResponse;
    }
  } catch {
    payload = undefined;
  }

  return {
    http_status: response.status,
    code: payload?.code ?? "INTERNAL_ERROR",
    message: payload?.message ?? (response.statusText || "request failed"),
    request_id: payload?.request_id ?? response.headers.get("X-Request-Id") ?? undefined,
    detail: payload?.detail
  };
}

export function isClientError(value: unknown): value is ClientError {
  return isObject(value) && typeof value.code === "string" && typeof value.message === "string";
}
