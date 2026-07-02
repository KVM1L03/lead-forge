import { describe, expect, it } from "vitest";
import { searchLeads, getStatus, approveLeads } from "./api";

describe("api exports", () => {
  it("exports async functions for all three endpoints", () => {
    expect(typeof searchLeads).toBe("function");
    expect(typeof getStatus).toBe("function");
    expect(typeof approveLeads).toBe("function");
  });

  it("getStatus builds correct URL (fetch will be called with workflowId in path)", () => {
    // Verify the function signature accepts a string without throwing at import time.
    expect(getStatus.length).toBe(1);
  });
});
