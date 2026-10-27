import { describe, expect, it } from "vitest";

import { practiceDatabase, practiceDatabases } from "./practiceDatabases";

describe("practiceDatabase", () => {
  it("keeps three databases for the practice tasks", () => {
    expect(practiceDatabases.map((database) => database.id)).toEqual(["shop", "library", "team"]);
    for (const database of practiceDatabases) {
      expect(database.tables.length).toBeGreaterThan(0);
    }
  });

  it("assigns the textbook, the library, and the team to different steps", () => {
    expect(practiceDatabase("tutorial", "select")?.id).toBe("shop");
    expect(practiceDatabase("patterns", "nullable-surprise")?.id).toBe("library");
    expect(practiceDatabase("patterns", "one-query")?.id).toBe("team");
  });
});
