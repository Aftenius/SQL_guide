import { Outlet } from "react-router";

import { Breadcrumbs } from "./Breadcrumbs";
import { Header } from "./Header";

export function RootLayout() {
  return (
    <>
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-20 focus:bg-card focus:px-3 focus:py-2"
      >
        К содержанию
      </a>
      <Header />
      <Breadcrumbs />
      <main id="content" className="mx-auto w-full max-w-5xl px-4 py-8 scroll-mt-24">
        <Outlet />
      </main>
    </>
  );
}
