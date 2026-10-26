import { Link, useLocation, useMatches } from "react-router";

import { breadcrumbItems } from "../breadcrumbs";

export function Breadcrumbs() {
  const matches = useMatches();
  const { pathname } = useLocation();
  const items = breadcrumbItems(matches);
  if (pathname === "/" || items.length < 2) return null;

  return (
    <nav aria-label="Навигационная цепочка">
      <ol className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
        {items.map((item, index) => {
          const last = index === items.length - 1;
          return (
            <li key={item.href} className="flex items-center gap-2">
              {index > 0 ? (
                <span aria-hidden="true" className="text-stone-400">
                  →
                </span>
              ) : null}
              {last ? (
                <span aria-current="page" className="font-bold text-pencil">
                  {item.label}
                </span>
              ) : (
                <Link to={item.href} className="inline-flex min-h-11 items-center text-stone-600 underline">
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
