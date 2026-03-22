import { parseClientError, type ClientError } from "./errors";

export interface RequestContext {
  bearerToken?: string | null;
  language?: string | null;
  requestId?: string | null;
}

export class HttpClientError extends Error {
  clientError: ClientError;

  constructor(clientError: ClientError) {
    super(clientError.message);
    this.name = "HttpClientError";
    this.clientError = clientError;
  }
}

function buildHeaders(context?: RequestContext, initHeaders?: HeadersInit): Headers {
  const headers = new Headers(initHeaders);

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (context?.bearerToken) {
    headers.set("Authorization", `Bearer ${context.bearerToken}`);
  }
  if (context?.language) {
    headers.set("X-User-Language", context.language);
  }
  if (context?.requestId) {
    headers.set("X-Request-Id", context.requestId);
  }

  return headers;
}

export async function fetchJson<T>(input: RequestInfo | URL, init: RequestInit = {}, context?: RequestContext): Promise<T> {
  const response = await fetch(input, {
    ...init,
    headers: buildHeaders(context, init.headers)
  });

  if (!response.ok) {
    throw new HttpClientError(await parseClientError(response));
  }

  return (await response.json()) as T;
}
