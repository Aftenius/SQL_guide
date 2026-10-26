/** Breadcrumb trail derived from the matched route handles. */

export type CrumbMatch = {
  pathname: string;
  handle?: unknown;
  params?: Record<string, string | undefined>;
};

export type Crumb = {
  href: string;
  label: string;
};

type CrumbHandle = {
  crumb?: string | ((match: CrumbMatch) => string | null);
};

export function breadcrumbItems(matches: readonly CrumbMatch[]): Crumb[] {
  const items: Crumb[] = [{ href: "/", label: "Главная" }];
  for (const match of matches) {
    const label = crumbLabel(match);
    if (label) items.push({ href: match.pathname, label });
  }
  return items;
}

function crumbLabel(match: CrumbMatch): string | null {
  if (!isCrumbHandle(match.handle) || match.handle.crumb === undefined) return null;
  const crumb = match.handle.crumb;
  return typeof crumb === "function" ? crumb(match) : crumb;
}

function isCrumbHandle(handle: unknown): handle is CrumbHandle {
  return typeof handle === "object" && handle !== null && "crumb" in handle;
}
