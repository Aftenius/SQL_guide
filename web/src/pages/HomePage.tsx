import { Link } from "react-router";

import { stepCount, trackPath, tracks } from "../catalog";
import { buttonClass, cardClass } from "../components/ui";
import { usePageTitle } from "../title";

export function HomePage() {
  usePageTitle("SQL Guide");

  return (
    <div className="grid gap-6">
      <section className="sticky-note max-w-2xl p-5">
        <p className="text-sm font-medium tracking-wide text-stone-600 uppercase">
          с первой выборки до отказоустойчивости
        </p>
        <h1 className="mt-1 text-4xl font-bold">SQL по одному адресу за шаг</h1>
        <p className="mt-3 text-stone-800">
          Сначала короткий учебник, потом паттерны запросов и схема, которая выдерживает рост. Прогресс остаётся в аккаунте.
        </p>
        <Link to="/learn/tutorial/introduction" className={`${buttonClass} mt-5`}>
          Начать учебник
        </Link>
      </section>
      <section aria-label="Разделы курса">
        <ul className="grid gap-4 sm:grid-cols-2">
          {tracks.map((track) => (
            <li key={track.slug}>
              <Link to={trackPath(track.slug)} className={cardClass}>
                <h2 className="text-2xl font-bold">{track.title}</h2>
                <p className="mt-2 text-stone-700">{track.summary}</p>
                <p className="mt-4 text-sm font-semibold text-indigo-700">{stepCount(track.lessons.length)}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
