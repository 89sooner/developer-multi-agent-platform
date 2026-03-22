import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderDirectEntry } from "./directEntry";

describe("health route", () => {
  it("renders connector cards from the backend health contract", async () => {
    renderDirectEntry("/health");

    expect(await screen.findByText("Backend health")).toBeInTheDocument();
    expect(screen.getByText("workspace repo connector online")).toBeInTheDocument();
    expect(screen.getByText("fallback docs connector")).toBeInTheDocument();
  });
});
