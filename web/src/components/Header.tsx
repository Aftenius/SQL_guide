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
    <header className="sketch-box bg-white p-3">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link to="/" className="flex min-w-0 items-center gap-3">
          <span
            aria-hidden="true"
            className="sketch-pill flex size-11 items-center justify-center bg-indigo-100 text-xl font-bold text-indigo-700"
          >
            ✎
          </span>
          <span>
            <span className="flex flex-wrap items-center gap-2 text-xl font-bold md:text-2xl">
              SQL Guide
              <span className="sketch-pill bg-yellow-200 px-2 py-0.5 text-xs text-stone-800">
                hand-crafted
              </span>
            </span>
            <span className="mt-0.5 block text-sm text-stone-600">
              интерактивный скетч-учебник баз данных
            </span>
          </span>
        </Link>
        {session.isPending ? (
          <span className="inline-block min-h-11 w-28" />
        ) : learner ? (
          <div className="flex min-w-0 items-center gap-2">
            <Link
              to="/profile"
              aria-current={pathname === "/profile" ? "page" : undefined}
              className={`sketch-button inline-flex min-h-11 max-w-48 items-center truncate px-3 text-sm font-semibold ${
                pathname === "/profile" ? "bg-yellow-200" : "bg-white"
              }`}
            >
              Профиль
            </Link>
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
      <nav aria-label="Разделы" className="mt-3 flex gap-2 overflow-x-auto pb-1">
        {tracks.map((track) => {
          const href = trackPath(track.slug);
          const here = pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={track.slug}
              to={href}
              aria-current={here ? "page" : undefined}
              className={`sketch-button inline-flex min-h-11 shrink-0 items-center px-3 text-sm font-semibold ${
                here ? "bg-yellow-200" : "bg-white"
              }`}
            >
              {track.title}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
