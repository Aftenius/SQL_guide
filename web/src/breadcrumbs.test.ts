import { describe, expect, it } from "vitest";

import { breadcrumbItems } from "./breadcrumbs";
import { coursePaths, lessonCrumb, stepCount } from "./catalog";
import { safeNext } from "./navigation";

describe("breadcrumbItems", () => {
  it("builds the trail from route handles", () => {
    const items = breadcrumbItems([
      { pathname: "/", handle: undefined },
      { pathname: "/learn", handle: { crumb: "Обучение" } },
      { pathname: "/learn/sql", handle: { crumb: "SQL" } },
      {
        pathname: "/learn/sql/select",
        params: { track: "sql", lesson: "select" },
        handle: { crumb: lessonCrumb },
      },
    ]);

    expect(items.map((item) => item.label)).toEqual([
      "Главная",
      "Обучение",
      "SQL",
      "Выборка",
    ]);
    expect(items.at(-1)?.href).toBe("/learn/sql/select");
  });

  it("drops an unknown lesson from the trail", () => {
    const items = breadcrumbItems([
      { pathname: "/learn/sql", handle: { crumb: "SQL" } },
      {
        pathname: "/learn/sql/missing",
        params: { track: "sql", lesson: "missing" },
        handle: { crumb: lessonCrumb },
      },
    ]);

    expect(items.map((item) => item.label)).toEqual(["Главная", "SQL"]);
  });
});

describe("coursePaths", () => {
  it("gives every lesson its own address", () => {
    const paths = coursePaths();
    expect(new Set(paths).size).toBe(paths.length);
    expect(paths).toContain("/learn/sql/select");
    expect(paths).toContain("/learn/scaling/sharding");
    expect(paths).toContain("/learn/architecture/split-brain");
  });
});

describe("stepCount", () => {
  it("uses Russian plural forms", () => {
    expect(stepCount(1)).toBe("1 шаг");
    expect(stepCount(3)).toBe("3 шага");
    expect(stepCount(7)).toBe("7 шагов");
    expect(stepCount(16)).toBe("16 шагов");
  });
});

describe("safeNext", () => {
  it("allows an in-app lesson and rejects external targets", () => {
    expect(safeNext("/learn/sql/joins")).toBe("/learn/sql/joins");
    expect(safeNext("https://example.com")).toBe("/learn");
    expect(safeNext("//example.com")).toBe("/learn");
    expect(safeNext("/login")).toBe("/learn");
    expect(safeNext(null)).toBe("/learn");
  });
});
