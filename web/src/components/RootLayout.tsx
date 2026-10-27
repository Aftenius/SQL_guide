import { Outlet } from "react-router";

import { Breadcrumbs } from "./Breadcrumbs";
import { Header, TrackNav } from "./Header";

export function RootLayout() {
  return (
    <div className="flex min-h-dvh flex-col">
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-40 focus:bg-white focus:px-3 focus:py-2"
      >
        К содержанию
      </a>
      <Header />
      <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-2 px-3 py-2 md:px-6">
        <TrackNav />
        <Breadcrumbs />
        <main id="content" className="flex-1 scroll-mt-24">
          <Outlet />
        </main>
        <footer className="flex flex-wrap items-center justify-between gap-2 border-t-2 border-dashed border-stone-300 pt-4 text-xs text-stone-600">
          <p>
            <span className="font-bold">SQL Guide</span>
          </p>
        </footer>
      </div>
    </div>
  );
}
