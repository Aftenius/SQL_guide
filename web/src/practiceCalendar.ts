/** Contribution calendar for solved days and scheduled reviews. */

export type SolvedMark = {
  date: string;
  solved: number;
};

export type CalendarCell = {
  date: string;
  solved: number;
  due: number;
  future: boolean;
};

export type CalendarWeek = {
  label: string;
  cells: CalendarCell[];
};

const PAST_WEEKS = 26;
const FUTURE_WEEKS = 4;

export function calendarWeeks(
  today: string,
  solved: readonly SolvedMark[],
  dueOn: readonly string[],
): CalendarWeek[] {
  const solvedByDay = new Map(solved.map((day) => [day.date, day.solved]));
  const dueByDay = new Map<string, number>();
  for (const date of dueOn) dueByDay.set(date, (dueByDay.get(date) ?? 0) + 1);
  const start = addDays(mondayOnOrBefore(utcDate(today)), -PAST_WEEKS * 7);
  const weeks: CalendarWeek[] = [];
  let previousMonth = -1;
  for (let week = 0; week < PAST_WEEKS + 1 + FUTURE_WEEKS; week += 1) {
    const monday = addDays(start, week * 7);
    const month = monday.getUTCMonth();
    const label = month === previousMonth ? "" : monthName(monday);
    previousMonth = month;
    const cells = Array.from({ length: 7 }, (_, day) => {
      const date = isoDate(addDays(monday, day));
      return {
        date,
        solved: solvedByDay.get(date) ?? 0,
        due: dueByDay.get(date) ?? 0,
        future: date > today,
      };
    });
    weeks.push({ label, cells });
  }
  return weeks;
}

export type CellTone = "empty" | "low" | "mid" | "high" | "due";

export function cellTone(cell: Pick<CalendarCell, "solved" | "due">): CellTone {
  if (cell.solved >= 4) return "high";
  if (cell.solved >= 2) return "mid";
  if (cell.solved >= 1) return "low";
  if (cell.due > 0) return "due";
  return "empty";
}

export function dayWord(count: number): string {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return `${count} день`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} дня`;
  return `${count} дней`;
}

export function formatPracticeDate(iso: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    timeZone: "UTC",
  }).format(utcDate(iso));
}

function utcDate(iso: string): Date {
  const [year, month, day] = iso.split("-").map(Number);
  return new Date(Date.UTC(year ?? 1970, (month ?? 1) - 1, day ?? 1));
}

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function addDays(date: Date, days: number): Date {
  const next = new Date(date);
  next.setUTCDate(next.getUTCDate() + days);
  return next;
}

function mondayOnOrBefore(date: Date): Date {
  return addDays(date, -((date.getUTCDay() + 6) % 7));
}

function monthName(date: Date): string {
  return new Intl.DateTimeFormat("ru-RU", { month: "short", timeZone: "UTC" })
    .format(date)
    .replace(".", "");
}
