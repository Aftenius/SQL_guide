/** Practice databases shared by the textbook and the pattern lessons. */

export type PracticeTable = {
  name: string;
  columns: string[];
  rows: string[][];
};

export type PracticeDatabase = {
  id: string;
  title: string;
  summary: string;
  tables: PracticeTable[];
};

export const practiceDatabases: PracticeDatabase[] = [
  {
    id: "shop",
    title: "Книжный магазин",
    summary: "Книги, авторы и заказы. Большинство уроков читает эту базу.",
    tables: [
      {
        name: "books",
        columns: ["id", "title", "year", "pages", "price", "isbn"],
        rows: [
          ["1", "Север", "2019", "320", "400", "978-5-0001"],
          ["2", "Юг", "2021", "180", "350", "978-5-0002"],
          ["3", "Восток", "2019", "90", "200", "978-5-0003"],
        ],
      },
      {
        name: "authors",
        columns: ["id", "name"],
        rows: [
          ["1", "Анна Ли"],
          ["2", "Марк Ной"],
        ],
      },
      {
        name: "book_authors",
        columns: ["book_id", "author_id"],
        rows: [
          ["1", "1"],
          ["2", "2"],
          ["3", "1"],
        ],
      },
      {
        name: "orders",
        columns: ["id", "book_id", "city", "copies", "created_at"],
        rows: [
          ["1", "1", "Казань", "2", "2026-10-20"],
          ["2", "1", "Пермь", "1", "2026-10-21"],
          ["3", "3", "Казань", "4", "2026-10-25"],
          ["4", "NULL", "Омск", "1", "2026-10-26"],
          ["5", "2", "NULL", "1", "2026-10-26"],
        ],
      },
    ],
  },
  {
    id: "library",
    title: "Библиотека",
    summary: "Читатели, экземпляры и выдачи. Здесь пустой город и связь без пары.",
    tables: [
      {
        name: "readers",
        columns: ["id", "name", "city"],
        rows: [
          ["1", "Ира", "Казань"],
          ["2", "Олег", "Пермь"],
          ["3", "Нина", "NULL"],
        ],
      },
      {
        name: "copies",
        columns: ["id", "title", "shelf"],
        rows: [
          ["1", "Север", "А-1"],
          ["2", "Юг", "А-2"],
          ["3", "Восток", "Б-1"],
        ],
      },
      {
        name: "loans",
        columns: ["id", "reader_id", "copy_id", "due_on"],
        rows: [
          ["1", "1", "1", "2026-11-01"],
          ["2", "2", "1", "2026-11-03"],
          ["3", "3", "NULL", "2026-11-20"],
        ],
      },
    ],
  },
  {
    id: "team",
    title: "Команда",
    summary: "Отделы и сотрудники. Здесь связь многие-к-одному и пустой отдел.",
    tables: [
      {
        name: "departments",
        columns: ["id", "name"],
        rows: [
          ["1", "Редакция"],
          ["2", "Склад"],
        ],
      },
      {
        name: "employees",
        columns: ["id", "name", "department_id", "salary"],
        rows: [
          ["1", "Аня", "1", "90000"],
          ["2", "Борис", "1", "70000"],
          ["3", "Вера", "2", "60000"],
          ["4", "Глеб", "NULL", "50000"],
        ],
      },
    ],
  },
];

const lessonDatabaseId: Record<string, string> = {
  "tutorial/introduction": "shop",
  "tutorial/select": "shop",
  "tutorial/where": "shop",
  "tutorial/where-logic": "shop",
  "tutorial/filter-sort": "shop",
  "tutorial/review": "shop",
  "tutorial/inner-join": "shop",
  "tutorial/outer-join": "shop",
  "tutorial/nulls": "shop",
  "tutorial/expressions": "shop",
  "tutorial/aggregates": "shop",
  "tutorial/group-by": "shop",
  "tutorial/execution-order": "shop",
  "tutorial/insert": "shop",
  "tutorial/update": "shop",
  "tutorial/delete": "shop",
  "patterns/row-multiplication": "shop",
  "patterns/select-star": "shop",
  "patterns/filter-before-join": "shop",
  "patterns/aggregate-before-join": "shop",
  "patterns/readable-query": "shop",
  "patterns/stable-keys": "shop",
  "patterns/foreign-keys": "shop",
  "patterns/normalize-then-copy": "shop",
  "patterns/index-for-query": "shop",
  "patterns/narrow-rows": "shop",
  "patterns/split-when-large": "shop",
  "patterns/reads-aside": "shop",
  "patterns/nullable-surprise": "library",
  "patterns/one-query": "team",
};

export function practiceDatabaseId(track: string, lesson: string): string {
  return lessonDatabaseId[`${track}/${lesson}`] ?? "shop";
}

export function practiceDatabase(track: string, lesson: string): PracticeDatabase | undefined {
  const id = lessonDatabaseId[`${track}/${lesson}`];
  return practiceDatabases.find((database) => database.id === id);
}
