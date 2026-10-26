import { Link, useLocation } from "react-router";

import { logoutAccount } from "../api";
import { trackPath, tracks } from "../catalog";
import { useRememberLearner, useSession } from "../session";
import { buttonClass, buttonQuietClass } from "./ui";

export function Header() {
  const session = useSession();
  const remember = useRememberLearner();
  const { pathname } = useLocation();
  const learner = session.data;

  async function logout() {
    await logoutAccount();
    remember(null);
  }

  return (
    <header className="sticky top-0 z-10 border-b border-line bg-paper/95 backdrop-blur">
      <div className="mx-auto max-w-5xl px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <Link to="/" className="font-serif text-xl font-semibold tracking-tight">
            SQL Guide
          </Link>
          {session.isPending ? (
            <span className="inline-block min-h-11 w-28" />
          ) : learner ? (
            <div className="flex min-w-0 items-center gap-2">
              <span className="max-w-40 truncate text-sm text-muted">{learner.email}</span>
              <button type="button" className={buttonQuietClass} onClick={() => void logout()}>
                Выйти
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login" className={buttonQuietClass}>
                Войти
              </Link>
              <Link to="/register" className={buttonClass}>
                Регистрация
              </Link>
            </div>
          )}
        </div>
        <nav aria-label="Разделы" className="-mx-4 mt-2 flex gap-1 overflow-x-auto px-4">
          {tracks.map((track) => {
            const href = trackPath(track.slug);
            const here = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={track.slug}
                to={href}
                aria-current={pathname === href ? "page" : undefined}
                className={`inline-flex min-h-11 shrink-0 items-center rounded-md px-3 text-sm ${
                  here ? "bg-card font-medium text-moss" : "text-muted hover:text-ink"
                }`}
              >
                {track.title}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
