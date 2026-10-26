import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";

import { loadPractice, type PracticeCalendar } from "../api";
import { findLesson, lessonPath } from "../catalog";
import { ModelSettings } from "../components/ModelSettings";
import { buttonClass } from "../components/ui";
import {
  calendarWeeks,
  cellTone,
  dayWord,
  formatPracticeDate,
  type CalendarCell,
  type CellTone,
} from "../practiceCalendar";
import { useSession } from "../session";
import { usePageTitle } from "../title";

const toneClass: Record<CellTone, string> = {
  empty: "bg-stone-200",
  low: "bg-emerald-300",
  mid: "bg-emerald-500",
  high: "bg-emerald-800",
  due: "bg-amber-300",
};

const weekdays = ["Пн", "", "Ср", "", "Пт", "", ""];

export function ProfilePage() {
  usePageTitle("Профиль");
  const session = useSession();
  const practice = useQuery({
    queryKey: ["practice"],
    queryFn: loadPractice,
    enabled: Boolean(session.data),
  });

  if (session.isPending) return <p className="text-sm text-stone-600">Открываем профиль.</p>;
  if (!session.data) {
    return (
      <section className="sketch-box max-w-xl bg-white p-5">
        <h1 className="text-3xl font-bold">Профиль</h1>
        <p className="mt-3 text-stone-700">Календарь решений хранится в аккаунте.</p>
        <Link to="/login?next=/profile" className={`${buttonClass} mt-5`}>
          Войти
        </Link>
      </section>
    );
  }

  return (
    <section className="grid gap-5">
      <header>
        <h1 className="text-3xl font-bold">Профиль</h1>
        <p className="mt-2 text-sm text-stone-600">{session.data.email}</p>
      </header>
      <ModelSettings />
      {practice.isPending ? <p className="text-sm text-stone-600">Собираем календарь.</p> : null}
      {practice.isError ? (
        <p className="sketch-box bg-rose-50 p-3 text-sm text-rose-800">
          Календарь не открылся. Обновите страницу.
        </p>
      ) : null}
      {practice.data ? <Calendar overview={practice.data} /> : null}
    </section>
  );
}

function Calendar({ overview }: { overview: PracticeCalendar }) {
  const weeks = calendarWeeks(
    overview.today,
    overview.days,
    overview.reviews.map((review) => review.due_on),
  );
  return (
    <>
      <div className="sketch-box overflow-x-auto bg-white p-4">
        <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
          <h2 className="text-sm font-bold">Календарь решений</h2>
          <p className="text-sm text-stone-600">
            {dayWord(overview.streak)} подряд · {dayWord(overview.days.length)} с задачами
          </p>
        </div>
        <div className="flex gap-2">
          <div className="mt-5 grid grid-rows-7 gap-1 text-[10px] leading-4 text-stone-500">
            {weekdays.map((label, index) => (
              <span key={index} className="flex h-4 items-center">
                {label}
              </span>
            ))}
          </div>
          <div>
            <div className="mb-1 flex gap-1">
              {weeks.map((week) => (
                <span key={week.cells[0]?.date} className="relative h-4 w-4">
                  <span className="absolute left-0 text-[10px] whitespace-nowrap text-stone-500">
                    {week.label}
                  </span>
                </span>
              ))}
            </div>
            <div className="flex gap-1" role="img" aria-label="Дни с решёнными задачами и будущие повторения">
              {weeks.map((week) => (
                <div key={week.cells[0]?.date} className="grid grid-rows-7 gap-1">
                  {week.cells.map((cell) => (
                    <Cell key={cell.date} cell={cell} today={overview.today} />
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
        <ul className="mt-4 flex flex-wrap gap-3 text-xs text-stone-600">
          <Legend tone="empty" label="пусто" />
          <Legend tone="low" label="1 задача" />
          <Legend tone="mid" label="2–3" />
          <Legend tone="high" label="4 и больше" />
          <Legend tone="due" label="повторение" />
        </ul>
      </div>
      <div className="sketch-box bg-white p-4">
        <h2 className="text-sm font-bold">Интервальные повторения</h2>
        <p className="mt-2 max-w-2xl text-sm text-stone-700">
          Первое решение возвращается на следующий день, второе — через 6 дней. Дальше
          промежуток растёт, пока шаг снова не отмечен решённым.
        </p>
        {overview.reviews.length === 0 ? (
          <p className="mt-4 text-sm text-stone-600">
            На доске ещё нет решённых шагов. Отметьте задачу, и день появится в календаре.
          </p>
        ) : (
          <ul className="mt-4 grid gap-2">
            {overview.reviews.map((review) => {
              const found = findLesson(review.track, review.lesson);
              const title = found?.lesson.title ?? review.lesson;
              const when =
                review.due_on === overview.today
                  ? "сегодня"
                  : formatPracticeDate(review.due_on);
              return (
                <li key={`${review.track}/${review.lesson}`}>
                  <Link
                    to={lessonPath(review.track, review.lesson)}
                    className="flex min-h-11 items-center justify-between gap-3 border-b border-dashed border-stone-300 py-2 text-sm"
                  >
                    <span className="font-semibold">{title}</span>
                    <span className="text-stone-600">
                      {when}
                      {review.due_on < overview.today ? " · пора повторить" : ""}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </>
  );
}

function Cell({ cell, today }: { cell: CalendarCell; today: string }) {
  const tone = cellTone(cell);
  const solved =
    cell.solved === 0 ? "нет решений" : cell.solved === 1 ? "1 задача" : `${cell.solved} задачи`;
  const due = cell.due > 0 ? `, повторений: ${cell.due}` : "";
  return (
    <span
      title={`${formatPracticeDate(cell.date)}: ${solved}${due}`}
      className={`block h-4 w-4 rounded-sm ${toneClass[tone]} ${
        cell.date === today ? "outline outline-2 outline-offset-1 outline-pencil" : ""
      }`}
    />
  );
}

function Legend({ tone, label }: { tone: CellTone; label: string }) {
  return (
    <li className="flex items-center gap-1.5">
      <span className={`block h-3.5 w-3.5 rounded-sm ${toneClass[tone]}`} />
      {label}
    </li>
  );
}
