import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderDirectEntry } from "./directEntry";

describe("trace route", () => {
  it("supports direct entry with auth", async () => {
    window.sessionStorage.setItem(
      "developer-multi-agent-platform/session",
      JSON.stringify({
        bearerToken: "sub=alice;repos=developer-multi-agent-platform;roles=developer",
        language: "ko",
        lastRunId: null
      })
    );

    renderDirectEntry("/runs/run_123/trace");

    expect(await screen.findByText("Trace scaffold")).toBeInTheDocument();
    expect(screen.getAllByText(/trace_123/)).toHaveLength(2);
  });
});
