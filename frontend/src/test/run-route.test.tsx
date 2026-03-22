import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import userEvent from "@testing-library/user-event";

import { renderDirectEntry } from "./directEntry";

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
