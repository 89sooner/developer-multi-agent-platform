import type { FeedbackRequest } from "./contracts/requests";
import type { FeedbackResponse } from "./contracts/responses";
import { fetchJson, type RequestContext } from "./http";

export function createFeedback(payload: FeedbackRequest, context?: RequestContext) {
  return fetchJson<FeedbackResponse>("/v1/feedback", { method: "POST", body: JSON.stringify(payload) }, context);
}
