import { Link, useParams } from "react-router";

import {
  findLesson,
  findTrack,
  lessonNeighbors,
  lessonPath,
  trackPath,
  tracks,
} from "../catalog";
import { SketchLesson } from "../components/SketchLesson";
import type { SketchMode } from "../components/SchemaCanvas";
import { buttonQuietClass, cardClass } from "../components/ui";
import { usePageTitle } from "../title";

export function TracksPage() {
  usePageTitle("Обучение");

  return (
    <section>
      <h1 className="text-4xl font-bold">Обучение</h1>
      <p className="mt-3 max-w-2xl text-base text-stone-600">
        Четыре раздела. Адрес шага остаётся, когда на доске появится проверка.
      </p>
      <ul className="mt-8 grid gap-4 sm:grid-cols-2">
        {tracks.map((track) => (
          <li key={track.slug}>
            <Link to={trackPath(track.slug)} className={`${cardClass} block hover:border-moss`}>
              <h2 className="text-2xl font-bold">{track.title}</h2>
              <p className="mt-2 text-stone-700">{track.summary}</p>
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
      <h1 className="text-4xl font-bold">{track.title}</h1>
      <p className="mt-3 max-w-2xl text-base text-stone-600">{track.summary}</p>
      <ol className="mt-8 grid gap-3">
        {track.lessons.map((lesson, index) => (
          <li key={lesson.slug}>
            <Link
              to={lessonPath(track.slug, lesson.slug)}
              className={`${cardClass} flex gap-4 hover:border-moss`}
            >
              <span className="text-xl font-semibold text-indigo-700">{index + 1}</span>
              <span>
                <span className="block font-bold">{lesson.title}</span>
                <span className="mt-1 block text-sm text-stone-700">{lesson.summary}</span>
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
    <SketchLesson
      badge={track.title}
      title={lesson.title}
      summary={lesson.summary}
      mode={sketchMode(lesson.slug)}
      track={track.slug}
      lesson={lesson.slug}
      previous={
        neighbors.previous
          ? { href: lessonPath(track.slug, neighbors.previous.slug), title: neighbors.previous.title }
          : undefined
      }
      next={
        neighbors.next
          ? { href: lessonPath(track.slug, neighbors.next.slug), title: neighbors.next.title }
          : undefined
      }
    />
  );
}

function sketchMode(slug: string): SketchMode {
  if (slug === "joins" || slug === "row-multiplication") return "join";
  if (slug === "aggregates" || slug === "execution-order") return "group";
  return "tables";
}

function Missing({ title, href, link }: { title: string; href: string; link: string }) {
  return (
    <section>
      <h1 className="text-4xl font-bold">{title}</h1>
      <Link to={href} className={`${buttonQuietClass} mt-6`}>
        {link}
      </Link>
    </section>
  );
}
