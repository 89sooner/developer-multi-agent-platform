import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SessionProvider, useSession } from "../session/SessionProvider";

function Harness() {
  const { bearerToken, setBearerToken, clearBearerToken } = useSession();
  return (
    <div>
      <span>{bearerToken || "empty"}</span>
      <button type="button" onClick={() => setBearerToken("token-value")}>set</button>
      <button type="button" onClick={clearBearerToken}>clear</button>
    </div>
  );
}

describe("session provider", () => {
  it("stores and clears token state", () => {
    render(
      <SessionProvider>
        <Harness />
      </SessionProvider>
    );

    fireEvent.click(screen.getByText("set"));
    expect(screen.getByText("token-value")).toBeInTheDocument();

    fireEvent.click(screen.getByText("clear"));
    expect(screen.getByText("empty")).toBeInTheDocument();
  });
});
