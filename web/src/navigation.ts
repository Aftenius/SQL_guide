/** Keep post-login redirects inside this site. */

export function safeNext(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/learn";
  if (value.includes("\\") || value.includes("://")) return "/learn";
  if (value.startsWith("/login") || value.startsWith("/register")) return "/learn";
  return value;
}
