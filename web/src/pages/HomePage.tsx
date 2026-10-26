import { Link } from "react-router";

import { stepCount, trackPath, tracks } from "../catalog";
import { cardClass, buttonClass } from "../components/ui";
import { usePageTitle } from "../title";

export function HomePage() {
  usePageTitle("SQL Guide");

  return (
    <div className="grid gap-10">
      <section className="max-w-2xl">
        <h1 className="font-serif text-4xl font-semibold tracking-tight sm:text-5xl">
          SQL по одному адресу за шаг
        </h1>
        <p className="mt-4 text-lg text-muted">
          Выборка, соединения, паттерны, масштаб и отказоустойчивость. У каждого шага
          постоянный адрес, а прогресс остаётся в аккаунте.
        </p>
        <Link to="/learn" className={`${buttonClass} mt-6`}>
          Открыть курс
        </Link>
      </section>
      <section aria-label="Разделы курса">
        <ul className="grid gap-4 sm:grid-cols-2">
          {tracks.map((track) => (
            <li key={track.slug}>
              <Link to={trackPath(track.slug)} className={`${cardClass} block hover:border-moss`}>
                <h2 className="font-serif text-2xl">{track.title}</h2>
                <p className="mt-2 text-muted">{track.summary}</p>
                <p className="mt-4 text-sm text-moss">{stepCount(track.lessons.length)}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
