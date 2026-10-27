import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Eraser } from "lucide-react";
import { useRef, useState, type KeyboardEvent, type UIEvent } from "react";
import { Link } from "react-router";

import { ApiError, recordSolve, runQuery, type QueryResult } from "../api";
import { highlightSql, type SqlTokenKind } from "../highlightSql";
import { type LessonBody, type LessonTable } from "../lessonBodies";
import { advanceSolved, lessonTasks, nextOpenTask, taskTables } from "../lessonTasks";
import { formatPracticeDate } from "../practiceCalendar";
import { practiceDatabaseId } from "../practiceDatabases";
import { useSession } from "../session";
import { buttonClass, buttonQuietClass } from "./ui";
import { SchemaCanvas, type SketchMode } from "./SchemaCanvas";

export function SketchLesson({
  badge,
  title,
  summary,
  body,
  mode,
  track,
  lesson,
  previous,
  next,
}: {
  badge: string;
  title: string;
  summary: string;
  body?: LessonBody;
  mode: SketchMode;
  track: string;
  lesson: string;
  previous?: { href: string; title: string };
  next?: { href: string; title: string };
}) {
  const tasks = lessonTasks(track, lesson);
  const tables = taskTables(track, lesson);
  const lessonId = `${track}/${lesson}`;
  const [query, setQuery] = useState("");
  const [pendingQuery, setPendingQuery] = useState(false);
  const [outcome, setOutcome] = useState<QueryOutcome | null>(null);
  const [solvedLesson, setSolvedLesson] = useState(lessonId);
  const [solved, setSolved] = useState<number[]>([]);
  if (solvedLesson !== lessonId) {
    setSolvedLesson(lessonId);
    setSolved([]);
    setOutcome(null);
    setQuery("");
  }
  const session = useSession();
  const client = useQueryClient();
  const solve = useMutation({
    mutationFn: () => recordSolve(track, lesson),
    onSuccess: async () => {
      await client.invalidateQueries({ queryKey: ["practice"] });
    },
  });

  async function run() {
    if (query.trim() === "") {
      setOutcome({ kind: "error", message: "Сначала напишите запрос." });
      return;
    }
    setPendingQuery(true);
    try {
      const result = await runQuery(
        practiceDatabaseId(track, lesson),
        query,
        tasks.map((task) => ({
          sql: task.solution ?? "",
          ordered: Boolean(task.ordered),
          probe: task.probe ?? "",
        })),
      );
      setOutcome({ kind: "rows", result });
      setSolved((current) => advanceSolved(current, result.passed, tasks));
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Запрос не выполнился.";
      setOutcome({ kind: "error", message });
    } finally {
      setPendingQuery(false);
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      run();
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <section className="sketch-box bg-white p-4" aria-label="Урок">
        <span className="sketch-pill bg-amber-300 px-2 py-0.5 text-xs font-bold tracking-wide uppercase">
          {badge}
        </span>
        <h1 className="text-2xl font-bold">{title}</h1>
        <p className="mt-2 text-base leading-relaxed text-stone-800">{summary}</p>
        {body
          ? body.paragraphs.map((paragraph) => (
              <p key={paragraph} className="mt-3 text-base leading-relaxed text-stone-800">
                {paragraph}
              </p>
            ))
          : null}
        {body?.syntax ? (
          <pre className="mt-4 w-fit max-w-full overflow-x-auto border-2 border-stone-800 bg-canvas p-3 font-code text-sm leading-6 whitespace-pre">
            <SqlCode source={body.syntax} />
          </pre>
        ) : null}
        {tables.length > 0 ? (
          <div className="mt-4 flex flex-wrap items-start gap-4">
            {tables.map((table) => (
              <ExampleTable key={table.name} table={table} />
            ))}
          </div>
        ) : tasks.length === 0 ? (
          <div className="mt-4" aria-label="Скетч схемы">
            <h2 className="mb-3 text-sm font-bold">Скетч схемы</h2>
            <div className="relative h-36 overflow-hidden rounded border-2 border-dashed border-stone-400 bg-canvas">
              <SchemaCanvas mode={mode} />
            </div>
          </div>
        ) : null}
        <div className={tasks.length > 0 ? "mt-4 grid items-start gap-4 lg:grid-cols-[minmax(0,7fr)_minmax(0,3fr)]" : "mt-4"}>
          <div>
            <h2 className="mb-2 text-sm font-bold text-stone-700">SQL запросчик</h2>
            <div className="relative">
              <SqlField value={query} onChange={setQuery} onKeyDown={onKeyDown} />
              <button
                type="button"
                aria-label="Очистить"
                className="absolute top-2 right-2 inline-flex size-9 items-center justify-center text-stone-500"
                onClick={() => setQuery("")}
              >
                <Eraser aria-hidden="true" className="size-4" />
              </button>
            </div>
            <div className="mt-3 flex justify-end">
              <button type="button" className={buttonClass} disabled={pendingQuery} onClick={() => void run()}>
                {pendingQuery ? "Выполняется…" : "Выполнить запрос"}
              </button>
            </div>
            <QueryOutcomeView outcome={outcome} />
            <SolveStep
              signedIn={Boolean(session.data)}
              sessionPending={session.isPending}
              pending={solve.isPending}
              error={solve.error}
              dueOn={solve.data?.due_on}
              counted={solve.data?.counted}
              onSolve={() => solve.mutate()}
            />
          </div>
          {tasks.length > 0 ? (
            <aside className="border-t-2 border-dashed border-stone-300 pt-3 lg:border-t-0 lg:border-l-2 lg:pt-0 lg:pl-4">
              <h2 className="text-sm font-bold">Задачи</h2>
              <ol className="mt-3 grid gap-3">
                {tasks.map((task, index) => {
                  const locked = index > nextOpenTask(solved, tasks);
                  return (
                    <li
                      key={task.prompt}
                      className={`flex items-start gap-2 text-sm leading-relaxed ${locked ? "text-stone-400" : ""}`}
                    >
                      <span className={`font-semibold ${locked ? "text-stone-400" : "text-indigo-700"}`}>
                        {index + 1}
                      </span>
                      <span className="flex-1">{task.prompt}</span>
                      {solved.includes(index) ? (
                        <Check className="mt-0.5 size-4 shrink-0 text-emerald-600" aria-label="Выполнено" />
                      ) : null}
                    </li>
                  );
                })}
              </ol>
            </aside>
          ) : null}
        </div>
      </section>

      <nav aria-label="Соседние шаги" className="flex flex-wrap gap-3">
        {previous ? (
          <Link to={previous.href} className={buttonQuietClass}>
            Предыдущая
          </Link>
        ) : null}
        {next ? (
          <Link
            to={next.href}
            className="sketch-button ml-auto inline-flex min-h-11 items-center justify-center bg-emerald-300 px-4 text-sm font-semibold text-pencil"
          >
            Следующая
          </Link>
        ) : null}
      </nav>
    </div>
  );
}

type QueryOutcome = { kind: "rows"; result: QueryResult } | { kind: "error"; message: string };

function QueryOutcomeView({ outcome }: { outcome: QueryOutcome | null }) {
  if (!outcome) return null;
  if (outcome.kind === "error") {
    return (
      <p className="mt-3 text-sm text-rose-800" aria-live="polite">
        {outcome.message}
      </p>
    );
  }
  if (outcome.result.columns.length === 0) {
    return (
      <p className="mt-3 text-sm text-stone-700" aria-live="polite">
        Команда выполнена.
      </p>
    );
  }
  return (
    <div className="mt-3 max-h-64 w-fit max-w-full overflow-auto" aria-live="polite">
      <table className="w-max border-2 border-stone-800 text-left text-xs">
        <thead className="bg-emerald-100">
          <tr>
            {outcome.result.columns.map((column, index) => (
              <th
                key={`${column}-${index}`}
                className="border border-stone-800 px-2 py-1 font-semibold whitespace-nowrap"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {outcome.result.rows.length === 0 ? (
            <tr>
              <td
                className="border border-stone-300 px-2 py-1 text-stone-500"
                colSpan={outcome.result.columns.length}
              >
                Пустой результат
              </td>
            </tr>
          ) : (
            outcome.result.rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((cell, index) => (
                  <td
                    key={`${rowIndex}-${index}`}
                    className="border border-stone-300 px-2 py-1 font-code whitespace-nowrap"
                  >
                    {cell === null ? <span className="text-stone-400">NULL</span> : String(cell)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

const tokenClass: Record<SqlTokenKind, string> = {
  keyword: "font-semibold text-indigo-700",
  string: "text-emerald-800",
  number: "text-amber-800",
  comment: "text-stone-500",
  plain: "text-stone-900",
};

function SqlCode({ source }: { source: string }) {
  return highlightSql(source).map((token, index) => (
    <span key={`${token.kind}-${index}`} className={tokenClass[token.kind]}>
      {token.text}
    </span>
  ));
}

function SqlField({
  value,
  onChange,
  onKeyDown,
}: {
  value: string;
  onChange: (value: string) => void;
  onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
}) {
  const backdrop = useRef<HTMLPreElement>(null);

  function syncScroll(event: UIEvent<HTMLTextAreaElement>) {
    if (!backdrop.current) return;
    backdrop.current.scrollTop = event.currentTarget.scrollTop;
    backdrop.current.scrollLeft = event.currentTarget.scrollLeft;
  }

  return (
    <div className="relative h-40 border-2 border-stone-800 bg-canvas">
      <pre
        ref={backdrop}
        aria-hidden="true"
        className="pointer-events-none h-full overflow-auto py-3 pr-12 pl-3 font-code text-sm leading-6 whitespace-pre-wrap"
      >
        {value ? <SqlCode source={value} /> : <span className="text-stone-400">Введите SELECT</span>}
        {"\n"}
      </pre>
      <label className="absolute inset-0">
        <span className="sr-only">Текст запроса</span>
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={onKeyDown}
          onScroll={syncScroll}
          spellCheck={false}
          className="h-full w-full resize-none bg-transparent py-3 pr-12 pl-3 font-code text-sm leading-6 whitespace-pre-wrap text-transparent caret-stone-900 outline-none"
        />
      </label>
    </div>
  );
}

function ExampleTable({ table }: { table: LessonTable }) {
  return (
    <div className="w-fit max-w-full overflow-x-auto">
      <p className="mb-1 text-xs font-bold tracking-wide text-stone-600 uppercase">{table.name}</p>
      <table className="w-max max-w-full border-2 border-stone-800 text-left text-xs">
        <thead className="bg-amber-100">
          <tr>
            {table.columns.map((column) => (
              <th key={column} className="border border-stone-800 px-2 py-1 font-semibold whitespace-nowrap">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row) => (
            <tr key={row.join("|")}>
              {row.map((cell, index) => (
                <td key={`${cell}-${index}`} className="border border-stone-300 px-2 py-1 font-code whitespace-nowrap">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
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
  if (sessionPending || !signedIn) return null;
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
