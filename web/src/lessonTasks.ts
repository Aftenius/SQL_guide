/** Practice tasks for one lesson. Tables listed here are the only ones shown. */

import { practiceDatabase, type PracticeTable } from "./practiceDatabases";

export type LessonTask = {
  prompt: string;
  tables: string[];
  solution?: string;
  ordered?: boolean;
  probe?: string;
};

type TaskSolution = {
  sql: string;
  ordered?: boolean;
  probe?: string;
};

function same(tables: string[], prompts: string[]): LessonTask[] {
  return prompts.map((prompt) => ({ prompt, tables }));
}

const tasks: Record<string, LessonTask[]> = {
  "tutorial/introduction": same(["books"], [
    "Выведите все строки из books.",
    "Выведите только столбец title.",
    "Выведите title и pages.",
  ]),
  "tutorial/select": same(["books"], [
    "Выведите title и year из books.",
    "Выведите строку книги с id = 2.",
    "Выведите названия всех книг.",
  ]),
  "tutorial/where": same(["books"], [
    "Оставьте книги, у которых pages больше 100.",
    "Найдите книги 2019 года.",
    "Найдите книгу с названием «Юг».",
  ]),
  "tutorial/where-logic": same(["books"], [
    "Найдите книги 2019 года длиннее 100 страниц.",
    "Найдите книги 2019 или 2021 года.",
    "Найдите книги короче 100 страниц или новее 2020 года.",
  ]),
  "tutorial/filter-sort": same(["books"], [
    "Выведите каждый год один раз.",
    "Выведите названия от самой длинной книги к самой короткой.",
    "Выведите две самые короткие книги.",
  ]),
  "tutorial/review": same(["books"], [
    "Найдите название самой короткой книги 2019 года.",
    "Выведите книги новее 2019 года, сначала дорогие.",
    "Выведите title и price книг дешевле 400.",
  ]),
  "tutorial/inner-join": same(["orders", "books"], [
    "Покажите city заказа рядом с title книги.",
    "Оставьте только заказы книги «Север».",
    "Посчитайте, сколько заказов нашлось у каждой книги. Книга без заказа не нужна.",
  ]),
  "tutorial/outer-join": same(["books", "orders"], [
    "Покажите все книги и город заказа. Книга без заказа тоже остаётся.",
    "Найдите книги, у которых заказов нет.",
    "Покажите заказы и название книги. Заказ без книги тоже остаётся.",
  ]),
  "tutorial/nulls": same(["orders"], [
    "Найдите заказы, у которых не указан book_id.",
    "Найдите заказы, у которых не указан город.",
    "Выведите заказы, у которых город заполнен.",
  ]),
  "tutorial/expressions": same(["books"], [
    "Покажите title и pages / 100.0 под именем hundreds.",
    "Покажите title и price * 1.1 под именем with_tax.",
    "Пометьте книгу короче 100 страниц как «тонкая», остальные как «обычная». Имя столбца — kind.",
  ]),
  "tutorial/aggregates": same(["orders"], [
    "Посчитайте сумму copies.",
    "Посчитайте, сколько заказов в таблице.",
    "Посчитайте среднее copies.",
  ]),
  "tutorial/group-by": same(["orders"], [
    "Посчитайте сумму copies по каждому городу.",
    "Посчитайте число заказов в каждом городе.",
    "Оставьте города, где сумма copies больше 2.",
  ]),
  "tutorial/execution-order": [
    { prompt: "Оставьте книги 2019 года и отсортируйте их по pages.", tables: ["books"] },
    { prompt: "Посчитайте сумму copies по городу и оставьте группы больше 2.", tables: ["orders"] },
    { prompt: "Дайте цене имя cost в SELECT и отсортируйте по этому имени.", tables: ["books"] },
  ],
  "tutorial/insert": same(["books"], [
    "Добавьте книгу «Запад», 2024 год, 210 страниц, цена 300, isbn 978-5-0004.",
    "Добавьте книгу «Север. Том 2» с тем же годом и ценой, что у «Север». Страниц 100, isbn 978-5-0005.",
    "Добавьте строку с id = 4 и сразу верните её id.",
  ]),
  "tutorial/update": same(["books"], [
    "Поставьте книге «Юг» 200 страниц.",
    "Поднимите цену «Север» до 450.",
    "Поставьте книге «Восток» 2020 год.",
  ]),
  "tutorial/delete": same(["books"], [
    "Удалите книгу с id = 3.",
    "Удалите книги короче 100 страниц.",
    "Сначала выберите книгу «Юг», затем удалите её по id.",
  ]),
  "tutorial/create-table": same([], [
    "Создайте таблицу readers с id, name и city. id — первичный ключ, name обязателен.",
    "Создайте таблицу shelves с id и code. code уникален.",
    "Создайте таблицу loans с id, reader_id и copy_id. Оба внешних столбца обязательны.",
  ]),
  "tutorial/alter-table": same(["books"], [
    "Добавьте в books необязательный столбец city типа text.",
    "Добавьте столбец reprint_year типа integer.",
    "Запретите пустой title, если ограничение ещё не стоит.",
  ]),
  "tutorial/drop-table": same([], [
    "Удалите таблицу readers.",
    "Напишите удаление таблицы shelves так, чтобы команда не падала, если таблицы уже нет.",
    "Напишите удаление loans без CASCADE.",
  ]),
  "tutorial/next": same([], [
    "Откройте урок про соединения и выпишите, чем INNER отличается от LEFT.",
    "Откройте паттерн про размножение строк и назовите, где сумма посчитается дважды.",
    "Выберите один запрос из учебника и перепишите SELECT * списком столбцов.",
  ]),
  "patterns/row-multiplication": same(["books", "orders"], [
    "Покажите, что после соединения «Север» встречается больше одного раза.",
    "Посчитайте сумму price после соединения с заказами и заметьте, что она завышена.",
    "Посчитайте число заказов по книге так, чтобы цена книги не удвоилась.",
  ]),
  "patterns/select-star": same(["books"], [
    "Перепишите SELECT * в список title, year.",
    "Выведите title, price и isbn без остальных столбцов.",
    "Назовите столбец, который сломает программу, если завтра его добавят, а запрос останется со звездой.",
  ]),
  "patterns/nullable-surprise": same(["readers"], [
    "Найдите читателей не из Казани обычным неравенством и посмотрите, кто пропал.",
    "Найдите читателей не из Казани, включая тех, у кого город не указан.",
    "Выведите только читателей без города.",
  ]),
  "patterns/filter-before-join": same(["orders", "books"], [
    "Оставьте заказы из Казани и присоедините названия книг.",
    "Присоедините к книгам только заказы из Перми. Книги без таких заказов не показывайте.",
    "Сделайте LEFT JOIN книг к заказам Казани так, чтобы «Юг» всё ещё был в результате.",
  ]),
  "patterns/aggregate-before-join": same(["orders", "books"], [
    "Посчитайте copies по book_id отдельным запросом.",
    "Присоедините к этой сумме title. У книги должна остаться одна строка.",
    "Рядом с названием покажите price из books, не из заказа.",
  ]),
  "patterns/readable-query": same(["books"], [
    "Вынесите фильтр year = 2019 в CTE и из него выберите названия.",
    "Вторым шагом оставьте из этого CTE книги длиннее 100 страниц.",
    "Дайте выражению price / pages имя и выведите его из последнего шага.",
  ]),
  "patterns/one-query": same(["employees", "departments"], [
    "Одним запросом достаньте имя сотрудника и название отдела.",
    "Оставьте сотрудников без отдела в том же запросе.",
    "Посчитайте число сотрудников в каждом отделе одним запросом, без цикла по отделам.",
  ]),
  "patterns/stable-keys": same(["books"], [
    "Покажите id и isbn. Это разные идентификаторы.",
    "Опишите таблицу books с суррогатным id и отдельной уникальностью на isbn.",
    "Найдите, какой столбец нельзя делать первичным ключом, потому что его правят люди.",
  ]),
  "patterns/foreign-keys": same(["orders", "books"], [
    "Найдите заказы, у которых book_id не находится в books.",
    "Опишите внешний ключ orders.book_id, который запрещает удалить книгу с заказами.",
    "Опишите тот же ключ так, чтобы удаление книги удаляло её заказы. Скажите, когда так делать не стоит.",
  ]),
  "patterns/normalize-then-copy": same(["books", "orders"], [
    "Покажите price из books рядом с заказом. Цена пока одна на книгу.",
    "Решите, где хранить цену книги и где цену на момент заказа.",
    "Напишите, какой столбец пришлось бы обновлять во многих строках, если цена лежит в каждом заказе.",
  ]),
  "patterns/index-for-query": same(["orders"], [
    "Напишите запрос: заказы Казани за 2026-10-26, новые сверху.",
    "Предложите составной индекс под этот запрос.",
    "Объясните, почему индекс только по created_at не заменяет индекс (city, created_at) для фильтра по городу.",
  ]),
  "patterns/narrow-rows": same(["books"], [
    "Выпишите столбцы, которые нужны списку книг на экране.",
    "Опишите отдельную таблицу для длинного текста книги один-к-одному с books.",
    "Назовите тип, который здесь уже уже, чем text: id, year, pages или price.",
  ]),
  "patterns/split-when-large": same(["orders"], [
    "Посчитайте число заказов по месяцу created_at.",
    "Опишите, по какому столбцу резать orders, если отчёты всегда идут за месяц.",
    "Напишите, почему случайный id плохой ключ для такой нарезки.",
  ]),
  "patterns/reads-aside": same(["orders"], [
    "Посчитайте число заказов за 2026-10-26. Это отчёт.",
    "Найдите заказ с id = 3. Это проверка конкретного факта.",
    "Напишите, какой из двух запросов можно отдать на реплику, а какой читают с основной базы.",
  ]),
};

const books = "id, title, year, pages, price, isbn";
const allBooks = `SELECT ${books} FROM books`;

const solutions: Record<string, Array<TaskSolution | null>> = {
  "tutorial/introduction": [
    { sql: allBooks },
    { sql: "SELECT title FROM books" },
    { sql: "SELECT title, pages FROM books" },
  ],
  "tutorial/select": [
    { sql: "SELECT title, year FROM books" },
    { sql: `${allBooks} WHERE id = 2` },
    { sql: "SELECT title FROM books" },
  ],
  "tutorial/where": [
    { sql: `${allBooks} WHERE pages > 100` },
    { sql: `${allBooks} WHERE year = 2019` },
    { sql: `${allBooks} WHERE title = 'Юг'` },
  ],
  "tutorial/where-logic": [
    { sql: `${allBooks} WHERE year = 2019 AND pages > 100` },
    { sql: `${allBooks} WHERE year = 2019 OR year = 2021` },
    { sql: `${allBooks} WHERE pages < 100 OR year > 2020` },
  ],
  "tutorial/filter-sort": [
    { sql: "SELECT DISTINCT year FROM books" },
    { sql: "SELECT title FROM books ORDER BY pages DESC", ordered: true },
    { sql: `${allBooks} ORDER BY pages LIMIT 2`, ordered: true },
  ],
  "tutorial/review": [
    { sql: "SELECT title FROM books WHERE year = 2019 ORDER BY pages LIMIT 1", ordered: true },
    { sql: `${allBooks} WHERE year > 2019 ORDER BY price DESC`, ordered: true },
    { sql: "SELECT title, price FROM books WHERE price < 400" },
  ],
  "tutorial/inner-join": [
    { sql: "SELECT orders.city, books.title FROM orders INNER JOIN books ON orders.book_id = books.id" },
    {
      sql: "SELECT orders.city, books.title FROM orders INNER JOIN books ON orders.book_id = books.id WHERE books.title = 'Север'",
    },
    {
      sql: "SELECT books.title, COUNT(*) FROM books INNER JOIN orders ON orders.book_id = books.id GROUP BY books.title",
    },
  ],
  "tutorial/outer-join": [
    { sql: "SELECT books.title, orders.city FROM books LEFT JOIN orders ON orders.book_id = books.id" },
    {
      sql: `SELECT books.${books.replaceAll(", ", ", books.")} FROM books LEFT JOIN orders ON orders.book_id = books.id WHERE orders.id IS NULL`,
    },
    { sql: "SELECT orders.id, books.title FROM orders LEFT JOIN books ON orders.book_id = books.id" },
  ],
  "tutorial/nulls": [
    { sql: "SELECT id, book_id FROM orders WHERE book_id IS NULL" },
    { sql: "SELECT id, city FROM orders WHERE city IS NULL" },
    { sql: "SELECT id, city FROM orders WHERE city IS NOT NULL" },
  ],
  "tutorial/expressions": [
    { sql: "SELECT title, pages / 100.0 AS hundreds FROM books" },
    { sql: "SELECT title, price * 1.1 AS with_tax FROM books" },
    { sql: "SELECT title, CASE WHEN pages < 100 THEN 'тонкая' ELSE 'обычная' END AS kind FROM books" },
  ],
  "tutorial/aggregates": [
    { sql: "SELECT SUM(copies) FROM orders" },
    { sql: "SELECT COUNT(*) FROM orders" },
    { sql: "SELECT AVG(copies) FROM orders" },
  ],
  "tutorial/group-by": [
    { sql: "SELECT city, SUM(copies) FROM orders GROUP BY city" },
    { sql: "SELECT city, COUNT(*) FROM orders GROUP BY city" },
    { sql: "SELECT city, SUM(copies) FROM orders GROUP BY city HAVING SUM(copies) > 2" },
  ],
  "tutorial/execution-order": [
    { sql: "SELECT title, pages FROM books WHERE year = 2019 ORDER BY pages", ordered: true },
    { sql: "SELECT city, SUM(copies) FROM orders GROUP BY city HAVING SUM(copies) > 2" },
    { sql: "SELECT title, price AS cost FROM books ORDER BY cost", ordered: true },
  ],
  "tutorial/insert": [
    {
      sql: "INSERT INTO books (id, title, year, pages, price, isbn) VALUES (4, 'Запад', 2024, 210, 300, '978-5-0004')",
      probe: "SELECT title, year, pages, price, isbn FROM books",
    },
    {
      sql: "INSERT INTO books (id, title, year, pages, price, isbn) VALUES (4, 'Север. Том 2', 2019, 100, 400, '978-5-0005')",
      probe: "SELECT title, year, pages, price, isbn FROM books",
    },
    {
      sql: "INSERT INTO books (id, title, year, pages, price, isbn) VALUES (4, 'Запад', 2024, 210, 300, '978-5-0004') RETURNING id",
    },
  ],
  "tutorial/update": [
    {
      sql: "UPDATE books SET pages = 200 WHERE title = 'Юг'",
      probe: "SELECT title, pages FROM books",
    },
    {
      sql: "UPDATE books SET price = 450 WHERE title = 'Север'",
      probe: "SELECT title, price FROM books",
    },
    {
      sql: "UPDATE books SET year = 2020 WHERE title = 'Восток'",
      probe: "SELECT title, year FROM books",
    },
  ],
  "tutorial/delete": [
    { sql: "DELETE FROM books WHERE id = 3", probe: "SELECT id FROM books" },
    { sql: "DELETE FROM books WHERE pages < 100", probe: "SELECT id FROM books" },
    { sql: "DELETE FROM books WHERE id = 2", probe: "SELECT id FROM books" },
  ],
  "tutorial/create-table": [
    {
      sql: "CREATE TABLE readers (id integer PRIMARY KEY, name text NOT NULL, city text)",
      ordered: true,
      probe:
        "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'readers' ORDER BY ordinal_position",
    },
    {
      sql: "CREATE TABLE shelves (id integer PRIMARY KEY, code text NOT NULL UNIQUE)",
      ordered: true,
      probe:
        "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'shelves' ORDER BY ordinal_position",
    },
    {
      sql: "CREATE TABLE loans (id integer PRIMARY KEY, reader_id integer NOT NULL, copy_id integer NOT NULL)",
      ordered: true,
      probe:
        "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'loans' ORDER BY ordinal_position",
    },
  ],
  "tutorial/alter-table": [
    {
      sql: "ALTER TABLE books ADD COLUMN city text",
      probe:
        "SELECT column_name FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'books' AND column_name = 'city'",
    },
    {
      sql: "ALTER TABLE books ADD COLUMN reprint_year integer",
      probe:
        "SELECT column_name FROM information_schema.columns WHERE table_schema = current_schema() AND table_name = 'books' AND column_name = 'reprint_year'",
    },
    null,
  ],
  "patterns/row-multiplication": [
    { sql: "SELECT books.title FROM books JOIN orders ON orders.book_id = books.id WHERE books.title = 'Север'" },
    { sql: "SELECT SUM(books.price) FROM books JOIN orders ON orders.book_id = books.id" },
    {
      sql: "SELECT books.title, books.price, COUNT(orders.id) FROM books JOIN orders ON orders.book_id = books.id GROUP BY books.id, books.title, books.price",
    },
  ],
  "patterns/select-star": [
    { sql: "SELECT title, year FROM books" },
    { sql: "SELECT title, price, isbn FROM books" },
    null,
  ],
  "patterns/nullable-surprise": [
    { sql: "SELECT name FROM readers WHERE city <> 'Казань'" },
    { sql: "SELECT name FROM readers WHERE city <> 'Казань' OR city IS NULL" },
    { sql: "SELECT name FROM readers WHERE city IS NULL" },
  ],
  "patterns/filter-before-join": [
    {
      sql: "SELECT orders.id, books.title FROM orders JOIN books ON orders.book_id = books.id WHERE orders.city = 'Казань'",
    },
    {
      sql: "SELECT books.title FROM books JOIN orders ON orders.book_id = books.id WHERE orders.city = 'Пермь'",
    },
    {
      sql: "SELECT books.title, orders.city FROM books LEFT JOIN orders ON orders.book_id = books.id AND orders.city = 'Казань'",
    },
  ],
  "patterns/aggregate-before-join": [
    { sql: "SELECT book_id, SUM(copies) FROM orders GROUP BY book_id" },
    {
      sql: "SELECT books.title, sums.copies FROM books JOIN (SELECT book_id, SUM(copies) AS copies FROM orders GROUP BY book_id) AS sums ON sums.book_id = books.id",
    },
    {
      sql: "SELECT books.title, books.price, sums.copies FROM books JOIN (SELECT book_id, SUM(copies) AS copies FROM orders GROUP BY book_id) AS sums ON sums.book_id = books.id",
    },
  ],
  "patterns/readable-query": [
    { sql: "WITH y2019 AS (SELECT title FROM books WHERE year = 2019) SELECT title FROM y2019" },
    {
      sql: "WITH y2019 AS (SELECT title, pages FROM books WHERE year = 2019) SELECT title FROM y2019 WHERE pages > 100",
    },
    { sql: "WITH costs AS (SELECT title, price / pages AS cost FROM books) SELECT title, cost FROM costs" },
  ],
  "patterns/one-query": [
    {
      sql: "SELECT employees.name, departments.name FROM employees JOIN departments ON employees.department_id = departments.id",
    },
    {
      sql: "SELECT employees.name, departments.name FROM employees LEFT JOIN departments ON employees.department_id = departments.id",
    },
    {
      sql: "SELECT departments.name, COUNT(employees.id) FROM departments LEFT JOIN employees ON employees.department_id = departments.id GROUP BY departments.name",
    },
  ],
  "patterns/stable-keys": [{ sql: "SELECT id, isbn FROM books" }, null, null],
  "patterns/foreign-keys": [
    {
      sql: "SELECT id FROM orders WHERE book_id IS NULL OR NOT EXISTS (SELECT 1 FROM books WHERE books.id = orders.book_id)",
    },
    null,
    null,
  ],
  "patterns/normalize-then-copy": [
    { sql: "SELECT orders.id, books.price FROM orders JOIN books ON orders.book_id = books.id" },
    null,
    null,
  ],
  "patterns/index-for-query": [
    {
      sql: "SELECT id FROM orders WHERE city = 'Казань' AND created_at = DATE '2026-10-26' ORDER BY created_at DESC",
      ordered: true,
    },
    null,
    null,
  ],
  "patterns/split-when-large": [
    { sql: "SELECT to_char(created_at, 'YYYY-MM') AS month, COUNT(*) FROM orders GROUP BY 1" },
    null,
    null,
  ],
  "patterns/reads-aside": [
    { sql: "SELECT COUNT(*) FROM orders WHERE created_at = DATE '2026-10-26'" },
    { sql: "SELECT id, book_id, city, copies, created_at FROM orders WHERE id = 3" },
    null,
  ],
};

export function lessonTasks(track: string, lesson: string): LessonTask[] {
  const key = `${track}/${lesson}`;
  const lessonSolutions = solutions[key] ?? [];
  return (tasks[key] ?? []).map((task, index) => {
    const solution = lessonSolutions[index];
    if (!solution) return task;
    return { ...task, solution: solution.sql, ordered: solution.ordered, probe: solution.probe };
  });
}

export function nextOpenTask(solved: readonly number[], items: readonly LessonTask[]): number {
  for (let index = 0; index < items.length; index += 1) {
    if (!items[index]?.solution || solved.includes(index)) continue;
    return index;
  }
  return items.length;
}

export function advanceSolved(
  solved: readonly number[],
  passed: readonly number[],
  items: readonly LessonTask[],
): number[] {
  const next = nextOpenTask(solved, items);
  if (!passed.includes(next)) return [...solved];
  return [...solved, next];
}

export function taskTables(track: string, lesson: string): PracticeTable[] {
  const database = practiceDatabase(track, lesson);
  const needed = new Set(lessonTasks(track, lesson).flatMap((task) => task.tables));
  if (!database || needed.size === 0) return [];
  return database.tables.filter((table) => needed.has(table.name));
}
