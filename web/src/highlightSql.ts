/** Color SQL so a keyword, a string, and a number are easy to tell apart. */

export type SqlTokenKind = "keyword" | "string" | "number" | "comment" | "plain";

export type SqlToken = {
  kind: SqlTokenKind;
  text: string;
};

const KEYWORDS = new Set([
  "add",
  "all",
  "alter",
  "analyze",
  "and",
  "as",
  "asc",
  "begin",
  "between",
  "by",
  "case",
  "check",
  "column",
  "commit",
  "create",
  "cross",
  "default",
  "delete",
  "desc",
  "distinct",
  "drop",
  "else",
  "end",
  "except",
  "exists",
  "explain",
  "from",
  "full",
  "group",
  "having",
  "ilike",
  "in",
  "inner",
  "insert",
  "intersect",
  "into",
  "is",
  "join",
  "key",
  "left",
  "like",
  "limit",
  "not",
  "null",
  "offset",
  "on",
  "or",
  "order",
  "over",
  "partition",
  "primary",
  "references",
  "right",
  "rollback",
  "select",
  "set",
  "table",
  "then",
  "union",
  "unique",
  "update",
  "values",
  "when",
  "where",
  "with",
]);

export function highlightSql(source: string): SqlToken[] {
  const tokens: SqlToken[] = [];
  let index = 0;
  while (index < source.length) {
    if (source.startsWith("--", index)) {
      const lineEnd = source.indexOf("\n", index);
      const stop = lineEnd === -1 ? source.length : lineEnd;
      tokens.push({ kind: "comment", text: source.slice(index, stop) });
      index = stop;
      continue;
    }
    const current = source[index] ?? "";
    if (current === "'") {
      let cursor = index + 1;
      while (cursor < source.length) {
        if (source[cursor] === "'" && source[cursor + 1] === "'") {
          cursor += 2;
          continue;
        }
        if (source[cursor] === "'") {
          cursor += 1;
          break;
        }
        cursor += 1;
      }
      tokens.push({ kind: "string", text: source.slice(index, cursor) });
      index = cursor;
      continue;
    }
    if (isDigit(current) && (index === 0 || !isWord(source[index - 1] ?? ""))) {
      let cursor = index + 1;
      while (cursor < source.length && /[0-9.]/.test(source[cursor] ?? "")) cursor += 1;
      tokens.push({ kind: "number", text: source.slice(index, cursor) });
      index = cursor;
      continue;
    }
    if (isWord(current)) {
      let cursor = index + 1;
      while (cursor < source.length && isWord(source[cursor] ?? "")) cursor += 1;
      const word = source.slice(index, cursor);
      tokens.push({
        kind: KEYWORDS.has(word.toLowerCase()) ? "keyword" : "plain",
        text: word,
      });
      index = cursor;
      continue;
    }
    tokens.push({ kind: "plain", text: current });
    index += 1;
  }
  return tokens;
}

function isDigit(char: string): boolean {
  return char >= "0" && char <= "9";
}

function isWord(char: string): boolean {
  return /[A-Za-z0-9_]/.test(char);
}
