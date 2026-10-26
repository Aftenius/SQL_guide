import { Outlet } from "react-router";

import { Breadcrumbs } from "./Breadcrumbs";
import { Header } from "./Header";

export function RootLayout() {
  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-6xl flex-col gap-5 p-3 md:p-6">
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-20 focus:bg-white focus:px-3 focus:py-2"
      >
        К содержанию
      </a>
      <Header />
      <Breadcrumbs />
      <main id="content" className="flex-1 scroll-mt-24">
        <Outlet />
      </main>
      <footer className="flex flex-wrap items-center justify-between gap-2 border-t-2 border-dashed border-stone-300 pt-4 text-xs text-stone-600">
        <p>
          <span className="font-bold">SQL Guide</span>
          <span aria-hidden="true"> · </span>
          <span>обучение на одной доске, адрес шага не меняется</span>
        </p>
      </footer>
    </div>
  );
}
