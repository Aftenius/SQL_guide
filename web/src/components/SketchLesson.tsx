import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type KeyboardEvent } from "react";
import { Link, useLocation } from "react-router";

import { ApiError, recordSolve } from "../api";
import { formatPracticeDate } from "../practiceCalendar";
import { useSession } from "../session";
import { buttonClass, buttonQuietClass } from "./ui";
import { SchemaCanvas, type SketchMode } from "./SchemaCanvas";

const snippets = ["SELECT ", "WHERE ", "ORDER BY ", "JOIN "];

export function SketchLesson({
  badge,
  title,
  summary,
  mode,
  track,
  lesson,
  previous,
  next,
}: {
  badge: string;
  title: string;
  summary: string;
  mode: SketchMode;
  track: string;
  lesson: string;
  previous?: { href: string; title: string };
  next?: { href: string; title: string };
}) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"idle" | "empty" | "held">("idle");
  const session = useSession();
  const client = useQueryClient();
  const solve = useMutation({
    mutationFn: () => recordSolve(track, lesson),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["practice"] });
    },
  });

  function run() {
    setStatus(query.trim() === "" ? "empty" : "held");
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      run();
    }
  }

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-12">
      <div className="flex flex-col gap-5 lg:col-span-5">
        <section className="sticky-note relative p-5">
          <div
            aria-hidden="true"
            className="absolute -top-3 left-1/2 flex size-6 -translate-x-1/2 items-center justify-center rounded-full border-2 border-stone-800 bg-red-400 text-[10px] font-bold text-white"
          >
            ×
          </div>
          <div className="mb-2 flex items-center justify-between gap-2">
            <span className="sketch-pill bg-amber-300 px-2 py-0.5 text-xs font-bold tracking-wide uppercase">
              {badge}
            </span>
            <span className="text-xs font-medium tracking-wide text-stone-600 uppercase">задание на доске</span>
          </div>
          <h1 className="text-2xl font-bold">{title}</h1>
          <p className="mt-2 text-sm leading-relaxed text-stone-800">{summary}</p>
          <p className="mt-3 bg-amber-100/90 p-2.5 text-xs">
            <span className="mb-1 block font-bold text-amber-950">На этой доске</span>
            Запрос сравнится по строкам результата, когда у шага появится набор в песочнице.
          </p>
          <SolveStep
            signedIn={Boolean(session.data)}
            sessionPending={session.isPending}
            pending={solve.isPending}
            error={solve.error}
            dueOn={solve.data?.due_on}
            counted={solve.data?.counted}
            onSolve={() => solve.mutate()}
          />
        </section>

        <section className="sketch-box flex flex-1 flex-col bg-white p-4" aria-label="Скетч схемы">
          <div className="mb-3 flex items-center justify-between border-b-2 border-dashed border-stone-300 pb-2">
            <h2 className="text-sm font-bold">Скетч схемы</h2>
            <span className="text-xs font-medium tracking-wide text-stone-500 uppercase">карандашом</span>
          </div>
          <div className="relative h-56 overflow-hidden rounded border-2 border-dashed border-stone-400 bg-canvas">
            <SchemaCanvas mode={mode} />
          </div>
        </section>
      </div>

      <div className="flex flex-col gap-5 lg:col-span-7">
        <section className="sketch-box bg-white p-5" aria-label="Редактор запроса">
          <div className="mb-3 flex items-center justify-between gap-2">
            <h2 className="text-sm font-bold text-stone-700">SQL запросчик</h2>
            <button type="button" className="sketch-pill min-h-11 bg-stone-100 px-3 text-xs" onClick={() => setQuery("")}>
              Очистить
            </button>
          </div>
          <label className="block">
            <span className="sr-only">Текст запроса</span>
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={onKeyDown}
              rows={6}
              spellCheck={false}
              placeholder="Введите SELECT"
              className="w-full border-2 border-stone-800 bg-canvas p-3 font-code text-sm leading-6 text-stone-900"
            />
          </label>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {snippets.map((snippet) => (
                <button
                  key={snippet}
                  type="button"
                  className="sketch-pill min-h-11 bg-stone-100 px-3 font-code text-xs"
                  onClick={() => setQuery((current) => `${current}${snippet}`)}
                >
                  {snippet.trim()}
                </button>
              ))}
            </div>
            <button type="button" className={buttonClass} onClick={run}>
              Выполнить запрос
            </button>
          </div>
        </section>

        <section className="sketch-box flex flex-1 flex-col bg-white p-5" aria-live="polite">
          <div className="mb-3 flex items-center justify-between border-b-2 border-dashed border-stone-300 pb-2">
            <h2 className="text-sm font-bold">Результат</h2>
            <span className="sketch-pill bg-stone-200 px-2.5 py-0.5 text-xs">
              {status === "idle" ? "Ожидание запроса" : status === "empty" ? "Пустой запрос" : "Записан на доске"}
            </span>
          </div>
          {status === "empty" ? (
            <p className="sketch-box bg-rose-50 p-3 text-sm text-rose-800">Сначала напишите запрос.</p>
          ) : null}
          {status === "held" ? (
            <p className="sketch-box bg-amber-100 p-3 text-sm">
              Текст запроса сохранён на этой странице. Сравнение строк сделает песочница.
            </p>
          ) : null}
          {status === "idle" ? (
            <div className="flex min-h-40 items-center justify-center border-2 border-stone-800 bg-canvas p-4 text-center">
              <p className="text-sm text-stone-500">
                Нажмите «Выполнить запрос», чтобы оставить его на доске.
              </p>
            </div>
          ) : null}
          <nav aria-label="Соседние шаги" className="mt-4 flex flex-wrap gap-3">
            {previous ? (
              <Link to={previous.href} className={buttonQuietClass}>
                {previous.title}
              </Link>
            ) : null}
            {next ? (
              <Link
                to={next.href}
                className="sketch-button inline-flex min-h-11 items-center justify-center bg-emerald-300 px-4 text-sm font-semibold text-pencil"
              >
                {next.title}
              </Link>
            ) : null}
          </nav>
        </section>
      </div>
    </div>
  );
}

function SolveStep({
  signedIn,
  sessionPending,
  pending,
  error,
  dueOn,
  counted,
  onSolve,
}: {
  signedIn: boolean;
  sessionPending: boolean;
  pending: boolean;
  error: unknown;
  dueOn?: string;
  counted?: boolean;
  onSolve: () => void;
}) {
  const { pathname } = useLocation();
  if (sessionPending) return null;
  if (!signedIn) {
    return (
      <Link
        to={`/login?next=${encodeURIComponent(pathname)}`}
        className={`${buttonQuietClass} mt-3`}
      >
        Войдите, чтобы засчитать день
      </Link>
    );
  }
  return (
    <div className="mt-3">
      <button
        type="button"
        disabled={pending}
        onClick={onSolve}
        className="sketch-button inline-flex min-h-11 items-center bg-emerald-300 px-4 text-sm font-semibold disabled:opacity-60"
      >
        Задача решена
      </button>
      {dueOn ? (
        <p className="mt-2 text-sm text-stone-700">
          {counted ? "День засчитан." : "Сегодня этот шаг уже засчитан."} Следующее повторение{" "}
          {formatPracticeDate(dueOn)}.{" "}
          <Link to="/profile" className="underline">
            Открыть календарь
          </Link>
        </p>
      ) : null}
      {error instanceof ApiError ? (
        <p className="mt-2 text-sm text-rose-800">{error.message}</p>
      ) : null}
    </div>
  );
}
