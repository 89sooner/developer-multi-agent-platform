import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { renderDirectEntry } from "./directEntry";

function seedSession() {
  window.sessionStorage.setItem(
    "developer-multi-agent-platform/session",
    JSON.stringify({
      bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
      language: "ko",
      lastRunId: null
    })
  );
}

describe("workflow release gate", () => {
  it("keeps the Phase 1 plan happy path working", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    await userEvent.clear(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."));
    await userEvent.type(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."), "Plan release gate regression");
    await userEvent.click(screen.getByRole("button", { name: "Submit plan request" }));

    expect(await screen.findByText("Plan result")).toBeInTheDocument();
  });

  it("supports review flow with validation and verdict rendering", async () => {
    seedSession();
    renderDirectEntry("/workflows/new?mode=review");

    await userEvent.clear(screen.getByPlaceholderText("Review the current workflow change for readiness and missing tests."));
    await userEvent.type(screen.getByPlaceholderText("Review the current workflow change for readiness and missing tests."), "Review the release candidate");
    await userEvent.type(screen.getByPlaceholderText("Optional raw diff input"), "diff --git a/frontend/src/routes/WorkflowsNewRoute.tsx");
    await userEvent.click(screen.getByRole("button", { name: "Submit review request" }));

    expect(await screen.findByText("Review the plan workflow release before merge.")).toBeInTheDocument();
    expect(screen.getByText("needs_changes")).toBeInTheDocument();
  });

  it("supports test-plan prefill from an existing plan run", async () => {
    seedSession();
    renderDirectEntry("/runs/run_123");

    expect(await screen.findByRole("button", { name: "Create test plan" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Create test plan" }));

    expect(await screen.findByText("Prefilled from the most recent plan result. You can edit every field before submitting.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Submit test-plan request" }));

    expect(await screen.findByText("Test-plan result")).toBeInTheDocument();
    expect(screen.getByText("Validate mode switching helpers")).toBeInTheDocument();
  });
});
