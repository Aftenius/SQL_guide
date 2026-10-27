import { describe, expect, it } from "vitest";

import { tracks } from "./catalog";
import { lessonTasks, taskTables } from "./lessonTasks";

describe("lessonTasks", () => {
  it("ends every textbook and pattern lesson with at least three tasks", () => {
    for (const slug of ["tutorial", "patterns"]) {
      const track = tracks.find((item) => item.slug === slug);
      expect(track).toBeDefined();
      for (const lesson of track?.lessons ?? []) {
        expect(lessonTasks(slug, lesson.slug).length, lesson.slug).toBeGreaterThanOrEqual(3);
      }
    }
  });

  it("shows only the tables a task needs", () => {
    expect(taskTables("tutorial", "select").map((table) => table.name)).toEqual(["books"]);
    expect(taskTables("tutorial", "inner-join").map((table) => table.name)).toEqual(["books", "orders"]);
    expect(taskTables("patterns", "nullable-surprise").map((table) => table.name)).toEqual(["readers"]);
    expect(taskTables("tutorial", "create-table")).toEqual([]);
  });
});
