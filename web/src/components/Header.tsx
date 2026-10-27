import { Link, useLocation } from "react-router";

import { logoutAccount } from "../api";
import { trackPath, tracks } from "../catalog";
import { useRememberLearner, useSession } from "../session";

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
    <header className="sticky top-0 z-30 border-b-2 border-stone-800 bg-paper">
      <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-2 px-3 py-1.5 md:px-6">
        <Link to="/" className="flex min-w-0 items-center gap-2">
          <span
            aria-hidden="true"
            className="sketch-pill flex size-8 items-center justify-center bg-indigo-100 text-base font-bold text-indigo-700"
          >
            ✎
          </span>
          <span className="min-w-0">
            <span className="flex flex-wrap items-center gap-2 text-lg font-bold">
              SQL Guide
              <span className="sketch-pill bg-yellow-200 px-1.5 py-0.5 text-[10px] text-stone-800">
                hand-crafted
              </span>
            </span>
            <span className="block text-xs leading-4 text-stone-600">
              интерактивный скетч-учебник баз данных
            </span>
          </span>
        </Link>
        {session.isPending ? (
          <span className="inline-block h-8 w-28" />
        ) : learner ? (
          <div className="flex min-w-0 items-center gap-2">
            <Link
              to="/profile"
              aria-current={pathname === "/profile" ? "page" : undefined}
              className={`sketch-button inline-flex h-8 max-w-48 items-center truncate px-3 text-sm font-semibold ${
                pathname === "/profile" ? "bg-yellow-200" : "bg-white"
              }`}
            >
              Профиль
            </Link>
            <button
              type="button"
              className="sketch-button inline-flex h-8 items-center bg-white px-3 text-sm font-semibold"
              onClick={() => void logout()}
            >
              Выйти
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link to="/login" className="sketch-button inline-flex h-8 items-center bg-white px-3 text-sm font-semibold">
              Войти
            </Link>
            <Link to="/register" className="sketch-button inline-flex h-8 items-center bg-yellow-300 px-3 text-sm font-semibold">
              Регистрация
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}

export function TrackNav() {
  const { pathname } = useLocation();

  return (
    <nav aria-label="Разделы" className="flex gap-2 overflow-x-auto">
      {tracks.map((track) => {
        const href = trackPath(track.slug);
        const here = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={track.slug}
            to={href}
            aria-current={here ? "page" : undefined}
            className={`sketch-button inline-flex h-8 shrink-0 items-center px-3 text-sm font-semibold ${
              here ? "bg-yellow-200" : "bg-white"
            }`}
          >
            {track.title}
          </Link>
        );
      })}
    </nav>
  );
}
