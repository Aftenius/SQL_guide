import { describe, expect, it } from "vitest";

import { calendarWeeks, cellTone, dayWord } from "./practiceCalendar";

describe("calendarWeeks", () => {
  it("marks solved days and a review later in the same week", () => {
    const weeks = calendarWeeks(
      "2026-10-26",
      [{ date: "2026-10-26", solved: 2 }],
      ["2026-10-27"],
    );
    const current = weeks.find((week) => week.cells[0]?.date === "2026-10-26");

    expect(weeks).toHaveLength(31);
    expect(current?.cells[0]).toMatchObject({ solved: 2, future: false });
    expect(current?.cells[1]).toMatchObject({ due: 1, future: true });
    expect(cellTone({ solved: 2, due: 0 })).toBe("mid");
    expect(cellTone({ solved: 0, due: 1 })).toBe("due");
  });
});

describe("dayWord", () => {
  it("uses Russian day plurals", () => {
    expect(dayWord(1)).toBe("1 день");
    expect(dayWord(2)).toBe("2 дня");
    expect(dayWord(5)).toBe("5 дней");
    expect(dayWord(11)).toBe("11 дней");
  });
});
