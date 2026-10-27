import { describe, expect, it } from "vitest";

import { highlightSql } from "./highlightSql";

describe("highlightSql", () => {
  it("marks a keyword, a string, and a number", () => {
    const tokens = highlightSql("SELECT title FROM books WHERE id = 1 AND title = 'Север'");
    expect(tokens.filter((token) => token.kind === "keyword").map((token) => token.text)).toEqual([
      "SELECT",
      "FROM",
      "WHERE",
      "AND",
    ]);
    expect(tokens.some((token) => token.kind === "number" && token.text === "1")).toBe(true);
    expect(tokens.some((token) => token.kind === "string" && token.text === "'Север'")).toBe(true);
  });

  it("does not treat a misspelled keyword as a keyword", () => {
    const tokens = highlightSql("SELCT title");
    expect(tokens[0]).toEqual({ kind: "plain", text: "SELCT" });
  });
});
