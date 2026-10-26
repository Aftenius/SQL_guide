import { useEffect } from "react";

export function usePageTitle(title: string): void {
  useEffect(() => {
    document.title = title === "SQL Guide" ? title : `${title} · SQL Guide`;
    return () => {
      document.title = "SQL Guide";
    };
  }, [title]);
}
