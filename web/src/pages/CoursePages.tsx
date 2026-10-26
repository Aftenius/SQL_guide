import { Link, useParams } from "react-router";

import {
  findLesson,
  findTrack,
  lessonNeighbors,
  lessonPath,
  trackPath,
  tracks,
} from "../catalog";
import { buttonQuietClass, cardClass } from "../components/ui";
import { usePageTitle } from "../title";

export function TracksPage() {
  usePageTitle("Обучение");

  return (
    <section>
      <h1 className="font-serif text-4xl">Обучение</h1>
      <p className="mt-3 max-w-2xl text-muted">
        Четыре раздела. Адрес шага не меняется, когда внутри появится практика.
      </p>
      <ul className="mt-8 grid gap-4 sm:grid-cols-2">
        {tracks.map((track) => (
          <li key={track.slug}>
            <Link to={trackPath(track.slug)} className={`${cardClass} block hover:border-moss`}>
              <h2 className="font-serif text-2xl">{track.title}</h2>
              <p className="mt-2 text-muted">{track.summary}</p>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function TrackPage() {
  const { track: trackSlug = "" } = useParams();
  const track = findTrack(trackSlug);
  usePageTitle(track?.title ?? "Раздел");
  if (!track) return <Missing title="Такого раздела нет" href="/learn" link="Ко всем разделам" />;

  return (
    <section>
      <h1 className="font-serif text-4xl">{track.title}</h1>
      <p className="mt-3 max-w-2xl text-muted">{track.summary}</p>
      <ol className="mt-8 grid gap-3">
        {track.lessons.map((lesson, index) => (
          <li key={lesson.slug}>
            <Link
              to={lessonPath(track.slug, lesson.slug)}
              className={`${cardClass} flex gap-4 hover:border-moss`}
            >
              <span className="font-medium text-moss">{index + 1}</span>
              <span>
                <span className="block font-medium">{lesson.title}</span>
                <span className="mt-1 block text-sm text-muted">{lesson.summary}</span>
              </span>
            </Link>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function LessonPage() {
  const { track: trackSlug = "", lesson: lessonSlug = "" } = useParams();
  const found = findLesson(trackSlug, lessonSlug);
  usePageTitle(found?.lesson.title ?? "Такого шага нет");
  if (!found) {
    return (
      <Missing
        title="Такого шага нет"
        href={findTrack(trackSlug) ? trackPath(trackSlug) : "/learn"}
        link="Вернуться к разделу"
      />
    );
  }
  const { track, lesson } = found;
  const neighbors = lessonNeighbors(track.slug, lesson.slug);

  return (
    <article className="grid gap-8 lg:grid-cols-[16rem_minmax(0,1fr)]">
      <nav aria-label="Шаги раздела" className="hidden lg:block">
        <ol className="grid gap-1">
          {track.lessons.map((item) => {
            const current = item.slug === lesson.slug;
            return (
              <li key={item.slug}>
                <Link
                  to={lessonPath(track.slug, item.slug)}
                  aria-current={current ? "page" : undefined}
                  className={`inline-flex min-h-11 items-center rounded-md px-3 text-sm ${
                    current ? "bg-card font-medium text-moss" : "text-muted hover:text-ink"
                  }`}
                >
                  {item.title}
                </Link>
              </li>
            );
          })}
        </ol>
      </nav>
      <div>
        <h1 className="font-serif text-4xl">{lesson.title}</h1>
        <p className="mt-4 max-w-2xl text-lg">{lesson.summary}</p>
        <section className={`${cardClass} mt-8`}>
          <h2 className="font-serif text-2xl">Практика</h2>
          <p className="mt-2 text-muted">
            На этом адресе откроется проверка запроса. Песочница сравнит строки результата.
          </p>
        </section>
        <nav aria-label="Соседние шаги" className="mt-6 flex flex-wrap gap-3">
          {neighbors.previous ? (
            <Link
              to={lessonPath(track.slug, neighbors.previous.slug)}
              className={buttonQuietClass}
            >
              {neighbors.previous.title}
            </Link>
          ) : null}
          {neighbors.next ? (
            <Link to={lessonPath(track.slug, neighbors.next.slug)} className={buttonQuietClass}>
              {neighbors.next.title}
            </Link>
          ) : null}
        </nav>
      </div>
    </article>
  );
}

function Missing({ title, href, link }: { title: string; href: string; link: string }) {
  return (
    <section>
      <h1 className="font-serif text-4xl">{title}</h1>
      <Link to={href} className={`${buttonQuietClass} mt-6`}>
        {link}
      </Link>
    </section>
  );
}
