import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { renderDirectEntry } from "./directEntry";

function seedSession(token = "sub=alice;repos=developer-multi-agent-platform;roles=developer") {
  window.sessionStorage.setItem(
    "developer-multi-agent-platform/session",
    JSON.stringify({ bearerToken: token, language: "ko", lastRunId: null })
  );
}

describe("workflows new route", () => {
  it("blocks submit until required fields are present", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    const button = screen.getByRole("button", { name: "Submit plan request" });
    await userEvent.click(button);

    expect(await screen.findByText("Fix the request input")).toBeInTheDocument();
    expect(screen.getByText("Task text is required.")).toBeInTheDocument();
  });

  it("submits a plan request and navigates to run detail", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    await userEvent.clear(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."));
    await userEvent.type(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."), "Implement Phase 1 plan route");

    await userEvent.click(screen.getByRole("button", { name: "Submit plan request" }));

    expect(await screen.findByText("Plan result")).toBeInTheDocument();
    expect(screen.getByText("Phase 1 shell baseline")).toBeInTheDocument();
    expect(screen.getByText("run_123")).toBeInTheDocument();
  });

  it("preserves form values on approval conflict and shows request id", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    await userEvent.clear(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."));
    await userEvent.type(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."), "Create PR for the new flow");
    await userEvent.click(screen.getByLabelText("create_pr"));
    await userEvent.click(screen.getByRole("button", { name: "Submit plan request" }));

    expect(await screen.findByText("approval token required for write actions")).toBeInTheDocument();
    expect(screen.getByText(/Request ID: req_conflict01/)).toBeInTheDocument();
    expect(screen.getByDisplayValue("Create PR for the new flow")).toBeInTheDocument();
  });

  it("surfaces forbidden guidance without clearing values", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    await userEvent.clear(screen.getByPlaceholderText("developer-multi-agent-platform"));
    await userEvent.type(screen.getByPlaceholderText("developer-multi-agent-platform"), "other-repo");
    await userEvent.clear(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."));
    await userEvent.type(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."), "Forbidden repo");
    await userEvent.click(screen.getByRole("button", { name: "Submit plan request" }));

    expect(await screen.findByText("repo scope violation")).toBeInTheDocument();
    expect(screen.getByDisplayValue("other-repo")).toBeInTheDocument();
  });

  it("surfaces unauthorized guidance when token is missing", async () => {
    renderDirectEntry("/workflows/new");

    await userEvent.clear(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."));
    await userEvent.type(screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels."), "Need auth");
    await userEvent.click(screen.getByRole("button", { name: "Submit plan request" }));

    expect(await screen.findByText("missing bearer token")).toBeInTheDocument();
    expect(screen.getByText(/Open the session token dialog/)).toBeInTheDocument();
  });

  it("renders backend validation detail without clearing the draft", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    const textarea = screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels.");
    await userEvent.clear(textarea);
    await userEvent.type(textarea, "trigger validation");
    await userEvent.click(screen.getByRole("button", { name: "Submit plan request" }));

    expect(await screen.findByText("body.task_text: Field required")).toBeInTheDocument();
    expect(screen.getByDisplayValue("trigger validation")).toBeInTheDocument();
  });

  it("prevents duplicate submits while loading", async () => {
    seedSession();
    renderDirectEntry("/workflows/new");

    const textarea = screen.getByPlaceholderText("Add a Phase 1 workflow form and semantic result panels.");
    await userEvent.clear(textarea);
    await userEvent.type(textarea, "Double-submit check");

    await userEvent.clear(textarea);
    await userEvent.type(textarea, "delay");

    const button = screen.getByRole("button", { name: "Submit plan request" });
    await userEvent.click(button);

    await waitFor(() => expect(screen.getByRole("button", { name: "Submitting plan request..." })).toBeDisabled());
  });

  it("blocks review submit until review context exists", async () => {
    seedSession();
    renderDirectEntry("/workflows/new?mode=review");

    await userEvent.clear(screen.getByPlaceholderText("Review the current workflow change for readiness and missing tests."));
    await userEvent.type(screen.getByPlaceholderText("Review the current workflow change for readiness and missing tests."), "Review release gate");
    await userEvent.click(screen.getByRole("button", { name: "Submit review request" }));

    expect(await screen.findByText("Review mode requires at least one of diff text, changed files, or PR URL.")).toBeInTheDocument();
  });

  it("submits a review request and navigates to review run detail", async () => {
    seedSession();
    renderDirectEntry("/workflows/new?mode=review");

    await userEvent.clear(screen.getByPlaceholderText("Review the current workflow change for readiness and missing tests."));
    await userEvent.type(screen.getByPlaceholderText("Review the current workflow change for readiness and missing tests."), "Review release gate");
    await userEvent.type(screen.getByPlaceholderText("Optional raw diff input"), "diff --git a/file");
    await userEvent.click(screen.getByRole("button", { name: "Submit review request" }));

    expect(await screen.findByText("Review the plan workflow release before merge.")).toBeInTheDocument();
    expect(screen.getByText("needs_changes")).toBeInTheDocument();
  });

  it("supports manual test-plan input without prefill", async () => {
    seedSession();
    renderDirectEntry("/workflows/new?mode=test-plan");

    await userEvent.type(screen.getByLabelText("Implementation plan"), "Validate review mode\nRender verdict chips");
    await userEvent.type(screen.getByLabelText("Impacted areas"), "frontend/src/routes/RunDetailRoute.tsx");
    await userEvent.click(screen.getByRole("button", { name: "Submit test-plan request" }));

    expect(await screen.findByText("Test-plan result")).toBeInTheDocument();
    expect(screen.getByText("Validate mode switching helpers")).toBeInTheDocument();
  });

  it("blocks invalid manual test-plan input", async () => {
    seedSession();
    renderDirectEntry("/workflows/new?mode=test-plan");

    await userEvent.click(screen.getByRole("button", { name: "Submit test-plan request" }));

    expect(await screen.findByText("At least one implementation-plan item is required.")).toBeInTheDocument();
    expect(screen.getByText("At least one impacted-area item is required.")).toBeInTheDocument();
  });
});
