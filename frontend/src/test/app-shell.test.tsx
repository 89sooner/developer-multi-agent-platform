import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderDirectEntry } from "./directEntry";

describe("app shell", () => {
  it("renders shell on workflow route", async () => {
    renderDirectEntry("/workflows/new");

    expect(await screen.findByText("Operator Console")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Plan workflow" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Health" })).toBeInTheDocument();
  });
});
