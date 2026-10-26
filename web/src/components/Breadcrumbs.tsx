import { ChevronRight } from "lucide-react";
import { Link, useLocation, useMatches } from "react-router";

import { breadcrumbItems } from "../breadcrumbs";

export function Breadcrumbs() {
  const matches = useMatches();
  const { pathname } = useLocation();
  const items = breadcrumbItems(matches);
  if (pathname === "/" || items.length < 2) return null;

  return (
    <nav aria-label="Навигационная цепочка" className="border-b border-line">
      <ol className="mx-auto flex max-w-5xl flex-wrap items-center gap-1 px-4 py-2 text-sm">
        {items.map((item, index) => {
          const last = index === items.length - 1;
          return (
            <li key={item.href} className="flex items-center gap-1">
              {index > 0 ? (
                <ChevronRight aria-hidden="true" className="size-4 text-muted" />
              ) : null}
              {last ? (
                <span aria-current="page" className="font-medium text-ink">
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.href}
                  className="inline-flex min-h-11 items-center text-muted hover:text-ink"
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
