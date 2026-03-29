import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import userEvent from "@testing-library/user-event";
import { waitFor } from "@testing-library/react";

import { renderDirectEntry } from "./directEntry";
import { server } from "./server";
import { runDetailFixture } from "./fixtures/contracts";

describe("run detail route", () => {
  it("requires auth for direct-entry protected routes", async () => {
    renderDirectEntry("/runs/run_123");

    expect(await screen.findByText("missing bearer token")).toBeInTheDocument();
    expect(screen.getByText(/Request ID: req_auth01/)).toBeInTheDocument();
  });

  it("renders protected run metadata after auth is stored", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_123");

    expect(await screen.findByText("Plan result")).toBeInTheDocument();
    expect(screen.getByText("run_123")).toBeInTheDocument();
    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.getByText("Create the plan form")).toBeInTheDocument();
    expect(screen.getAllByText("frontend/src/routes/RunDetailRoute.tsx")).toHaveLength(2);
    expect(screen.getByText("Result completed with limited backend context")).toBeInTheDocument();
    expect(screen.getByText("trace_123")).toBeInTheDocument();
    expect(screen.getByText("gpt-5.4")).toBeInTheDocument();
    expect(screen.getByText("orchestrator: v1")).toBeInTheDocument();
    expect(screen.getByText("requirements: v1")).toBeInTheDocument();
    expect(screen.getByText("developer-multi-agent-platform")).toBeInTheDocument();
  });

  it("supports raw payload inspectability on the run route", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_123");

    expect(await screen.findByRole("button", { name: "Show raw payloads" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Show raw payloads" }));
    expect(screen.getByText("Raw payloads")).toBeInTheDocument();
    expect(screen.getByText("Request payload")).toBeInTheDocument();
    expect(screen.getByText("Result payload")).toBeInTheDocument();
    expect(screen.getByText(/"task_text": "phase 0 shell"/)).toBeInTheDocument();
    expect(screen.getByText(/"summary": "Phase 1 shell baseline"/)).toBeInTheDocument();
  });

  it("fetches run detail only once after storing lastRunId", async () => {
    let runFetchCount = 0;

    server.use(
      http.get("/v1/workflows/:runId", ({ params, request }) => {
        runFetchCount += 1;

        const auth = request.headers.get("Authorization");
        if (!auth) {
          return HttpResponse.json({ code: "UNAUTHORIZED", message: "missing bearer token", request_id: "req_auth01" }, { status: 401 });
        }

        return HttpResponse.json({ ...runDetailFixture, run_id: String(params.runId) });
      })
    );

    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_123");

    expect(await screen.findByText("Plan result")).toBeInTheDocument();

    await waitFor(
      async () => {
        await new Promise((resolve) => setTimeout(resolve, 50));
        expect(runFetchCount).toBe(1);
      },
      { timeout: 200 }
    );
  });

  it("shows a generic error banner when the run fetch fails before an HTTP response", async () => {
    server.use(
      http.get("/v1/workflows/:runId", () => HttpResponse.error())
    );

    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_123");

    expect(await screen.findByText("REQUEST_FAILED")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("Failed to fetch");
  });

  it("shows forbidden state for protected runs outside scope", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/forbidden");

    expect(await screen.findByText("repo scope violation")).toBeInTheDocument();
    expect(screen.getByText("This repo or run is outside the current bearer scope.")).toBeInTheDocument();
    expect(screen.getByText(/Request ID: req_forbid01/)).toBeInTheDocument();
  });

  it("shows not found state for missing runs", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/missing");

    expect(await screen.findByText("run not found")).toBeInTheDocument();
    expect(screen.getByText("The requested backend resource was not found.")).toBeInTheDocument();
    expect(screen.getByText(/Request ID: req_missing01/)).toBeInTheDocument();
  });

  it("renders review results with verdict, findings, and evidence", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_review_123");

    expect(await screen.findByText("Review the plan workflow release before merge.")).toBeInTheDocument();
    expect(screen.getByText("needs_changes")).toBeInTheDocument();
    expect(screen.getByText("Add a route-level 404 test for run detail.")).toBeInTheDocument();
    expect(screen.getByText("review connector degraded to local context")).toBeInTheDocument();
  });

  it("renders test-plan sections from a test-plan run", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_test_plan_123");

    expect(await screen.findByText("Test-plan result")).toBeInTheDocument();
    expect(screen.getByText("Validate mode switching helpers")).toBeInTheDocument();
    expect(screen.getByText("test plan generated from partial context")).toBeInTheDocument();
  });
});
