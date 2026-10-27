/** Stable course map. URLs are derived from these slugs. */

export type Lesson = {
  slug: string;
  title: string;
  summary: string;
};

export type Track = {
  slug: string;
  title: string;
  summary: string;
  lessons: Lesson[];
};

export const tracks: Track[] = [
  {
    slug: "tutorial",
    title: "Учебник",
    summary: "Короткие уроки: от первой выборки до создания таблиц.",
    lessons: [
      {
        slug: "introduction",
        title: "Что такое SQL",
        summary: "Таблица, столбцы и зачем вообще писать запрос.",
      },
      {
        slug: "select",
        title: "Выборка столбцов",
        summary: "SELECT называет столбцы, FROM называет таблицу.",
      },
      {
        slug: "where",
        title: "Условие WHERE",
        summary: "Сравнение оставляет только подходящие строки.",
      },
      {
        slug: "where-logic",
        title: "AND, OR и IN",
        summary: "Несколько условий складывают в одно.",
      },
      {
        slug: "filter-sort",
        title: "Фильтр и сортировка",
        summary: "DISTINCT, ORDER BY и LIMIT доводят результат до нужного вида.",
      },
      {
        slug: "review",
        title: "Повторение выборки",
        summary: "Один запрос собирает фильтр, столбцы и порядок.",
      },
      {
        slug: "inner-join",
        title: "Внутреннее соединение",
        summary: "INNER JOIN оставляет только строки, у которых нашлась пара.",
      },
      {
        slug: "outer-join",
        title: "Внешнее соединение",
        summary: "LEFT JOIN сохраняет строки без пары.",
      },
      {
        slug: "nulls",
        title: "NULL",
        summary: "Пустое значение не находится обычным сравнением.",
      },
      {
        slug: "expressions",
        title: "Выражения",
        summary: "В выборке можно посчитать новое значение и дать ему имя.",
      },
      {
        slug: "aggregates",
        title: "Агрегаты",
        summary: "COUNT, SUM, AVG, MIN и MAX сворачивают строки в число.",
      },
      {
        slug: "group-by",
        title: "Группировка",
        summary: "GROUP BY считает агрегат по группам, HAVING фильтрует группы.",
      },
      {
        slug: "execution-order",
        title: "Порядок выполнения",
        summary: "База идёт FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT.",
      },
      {
        slug: "insert",
        title: "Вставка строк",
        summary: "INSERT добавляет строки в перечисленные столбцы.",
      },
      {
        slug: "update",
        title: "Обновление строк",
        summary: "UPDATE меняет значения, WHERE ограничивает строки.",
      },
      {
        slug: "delete",
        title: "Удаление строк",
        summary: "DELETE снимает строки, которые попали под WHERE.",
      },
      {
        slug: "create-table",
        title: "Создание таблицы",
        summary: "CREATE TABLE задаёт столбцы, типы и ключи.",
      },
      {
        slug: "alter-table",
        title: "Изменение таблицы",
        summary: "ALTER TABLE добавляет столбец или ограничение к живой таблице.",
      },
      {
        slug: "drop-table",
        title: "Удаление таблицы",
        summary: "DROP TABLE убирает таблицу целиком, не отдельные строки.",
      },
      {
        slug: "next",
        title: "Что дальше",
        summary: "Куда идти после первой выборки: глубже в SQL и в паттерны.",
      },
    ],
  },
  {
    slug: "sql",
    title: "SQL",
    summary: "Модель, типы, выборка, соединения и окна.",
    lessons: [
      {
        slug: "relational-model",
        title: "Реляционная модель и нормализация",
        summary: "1НФ–3НФ убирают повторы. Денормализация возвращает копию только осознанно.",
      },
      {
        slug: "ddl-types",
        title: "DDL и типы данных",
        summary: "int и bigint, text вместо varchar, timestamptz, uuid, jsonb и numeric.",
      },
      {
        slug: "constraints",
        title: "Ограничения целостности",
        summary: "PK, FK с ON DELETE и ON UPDATE, UNIQUE с NULL, CHECK и NOT NULL.",
      },
      {
        slug: "select",
        title: "SELECT, фильтрация и сортировка",
        summary: "WHERE, IN, BETWEEN, LIKE и ILIKE, ORDER BY и положение NULLS.",
      },
      {
        slug: "joins",
        title: "Соединения",
        summary: "INNER, LEFT, RIGHT, FULL, CROSS и self-join. WHERE после LEFT JOIN отрезает пустые совпадения.",
      },
      {
        slug: "aggregates",
        title: "Агрегация",
        summary: "GROUP BY, HAVING, COUNT, SUM, AVG, MIN, MAX, FILTER и DISTINCT.",
      },
      {
        slug: "subqueries",
        title: "Подзапросы и EXISTS",
        summary: "Коррелированный подзапрос, IN против EXISTS и производные таблицы.",
      },
      {
        slug: "set-operations",
        title: "Множественные операции",
        summary: "UNION, INTERSECT и EXCEPT складывают результаты по строкам.",
      },
      {
        slug: "cte",
        title: "CTE и рекурсия",
        summary: "WITH именует шаг, WITH RECURSIVE идёт по дереву, MATERIALIZED считает его сразу.",
      },
      {
        slug: "windows",
        title: "Оконные функции",
        summary: "PARTITION BY, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, кадры ROWS и RANGE.",
      },
      {
        slug: "upsert",
        title: "Upsert и конфликты",
        summary: "ON CONFLICT DO UPDATE и DO NOTHING, значения конфликта лежат в excluded.",
      },
      {
        slug: "pagination",
        title: "Пагинация",
        summary: "LIMIT и OFFSET пропускают уже прочитанные строки. Keyset идёт от последней увиденной.",
      },
    ],
  },
  {
    slug: "patterns",
    title: "Паттерны",
    summary: "Как писать запрос, чтобы он не врал, и как собрать базу, которая выдержит рост.",
    lessons: [
      {
        slug: "row-multiplication",
        title: "Размножение строк",
        summary: "Соединение один-ко-многим повторяет левую строку на каждое совпадение.",
      },
      {
        slug: "select-star",
        title: "SELECT *",
        summary: "Звезда тащит лишние столбцы и ломается, когда таблица меняется.",
      },
      {
        slug: "nullable-surprise",
        title: "Сюрпризы NULL",
        summary: "Фильтр «не равно» выбрасывает строки, в которых значения нет.",
      },
      {
        slug: "filter-before-join",
        title: "Сначала фильтр, потом соединение",
        summary: "Лишние строки отрезают до JOIN. У LEFT JOIN фильтр правой стороны стоит в ON.",
      },
      {
        slug: "aggregate-before-join",
        title: "Считать до соединения",
        summary: "Агрегат считают по своей таблице, к родителю присоединяют уже одну строку.",
      },
      {
        slug: "readable-query",
        title: "Запрос, который можно прочитать",
        summary: "CTE делит запрос на шаги с именами. У выражения есть алиас.",
      },
      {
        slug: "one-query",
        title: "Один запрос вместо цикла",
        summary: "Связанные строки забирают одним запросом, а не по штуке из приложения.",
      },
      {
        slug: "stable-keys",
        title: "Ключ, который не меняется",
        summary: "Суррогатный ключ не зависит от названия или почты, которые правят люди.",
      },
      {
        slug: "foreign-keys",
        title: "Связь, которая не теряет строки",
        summary: "Внешний ключ и явное ON DELETE не дают ссылке указывать в пустоту.",
      },
      {
        slug: "normalize-then-copy",
        title: "Нормализовать, потом копировать",
        summary: "Факт хранят в одном месте. Копию кладут рядом только вместе с правилом обновления.",
      },
      {
        slug: "index-for-query",
        title: "Индекс под конкретный запрос",
        summary: "Индекс начинают с столбцов фильтра. Лишний индекс замедляет запись.",
      },
      {
        slug: "narrow-rows",
        title: "Узкие строки",
        summary: "Частые поля держат короткими. Большой текст уносят в соседнюю таблицу.",
      },
      {
        slug: "split-when-large",
        title: "Делить большую таблицу",
        summary: "Партиция по времени снимает старые данные целиком, а не по строке.",
      },
      {
        slug: "reads-aside",
        title: "Чтение отдельно от записи",
        summary: "Отчёт уходит на реплику. Проверка только что записанного факта читает основную базу.",
      },
    ],
  },
  {
    slug: "transactions",
    title: "Транзакции",
    summary: "ACID, изоляция и блокировки строк.",
    lessons: [
      {
        slug: "acid",
        title: "Транзакции и ACID",
        summary: "BEGIN, COMMIT и ROLLBACK держат набор изменений. SAVEPOINT откатывает только хвост.",
      },
      {
        slug: "isolation",
        title: "Уровни изоляции и аномалии",
        summary:
          "Read Committed, Repeatable Read и Serializable. Lost update, non-repeatable read, phantom, write skew. Ошибка 40001 просит повтор.",
      },
      {
        slug: "row-locks",
        title: "Блокировки строк",
        summary: "FOR UPDATE, FOR SHARE и FOR NO KEY UPDATE. Взаимное ожидание заканчивается deadlock.",
      },
    ],
  },
  {
    slug: "planner",
    title: "План",
    summary: "Индексы, EXPLAIN и то, как PostgreSQL хранит строки.",
    lessons: [
      {
        slug: "btree",
        title: "Индексы B-tree",
        summary: "Индекс помогает, когда условие селективно и начинается с левого столбца. Запись платит за каждый индекс.",
      },
      {
        slug: "index-shapes",
        title: "Составные, частичные и функциональные индексы",
        summary: "Порядок столбцов, WHERE в определении индекса и выражение, по которому ищут.",
      },
      {
        slug: "covering-indexes",
        title: "Покрывающие индексы",
        summary: "INCLUDE держит лишние столбцы в индексе. Index only scan обходится без heap fetch.",
      },
      {
        slug: "specialized-indexes",
        title: "Специализированные индексы",
        summary: "GIN для jsonb и массивов, BRIN для упорядоченных диапазонов, GiST и hash.",
      },
      {
        slug: "explain",
        title: "EXPLAIN и EXPLAIN ANALYZE",
        summary: "Cost — оценка планировщика, actual — факт. BUFFERS и расхождение rows показывают, где план врёт.",
      },
      {
        slug: "join-algorithms",
        title: "Алгоритмы соединений",
        summary: "Nested Loop для малого числа совпадений, Hash Join для больших наборов, Merge Join для уже упорядоченных.",
      },
      {
        slug: "planner-stats",
        title: "Статистика планировщика",
        summary: "ANALYZE обновляет pg_stats. CREATE STATISTICS описывает связь столбцов.",
      },
      {
        slug: "query-optimization",
        title: "Оптимизация запросов",
        summary: "Условие должно быть sargable. Функция на столбце обходит индекс. N+1 зовёт базу на каждую строку.",
      },
      {
        slug: "mvcc",
        title: "MVCC",
        summary: "xmin и xmax отмечают версию строки. UPDATE пишет новую строку, старая остаётся до очистки.",
      },
      {
        slug: "vacuum",
        title: "VACUUM и bloat",
        summary: "AUTOVACUUM убирает мёртвые версии. Visibility map открывает index only scan. XID wraparound останавливает запись.",
      },
      {
        slug: "wal",
        title: "WAL и checkpoints",
        summary: "Журнал доносит изменение до диска. LSN отмечает место в журнале, checkpoint сбрасывает буферы.",
      },
      {
        slug: "memory",
        title: "Память PostgreSQL",
        summary: "shared_buffers держит страницы, work_mem — сортировку и хеш, maintenance_work_mem — VACUUM и индекс.",
      },
      {
        slug: "partitioning",
        title: "Партиционирование",
        summary: "RANGE, LIST и HASH делят таблицу. Partition pruning отбрасывает лишние части. DETACH снимает секцию.",
      },
    ],
  },
  {
    slug: "operations",
    title: "Эксплуатация",
    summary: "Очереди, ORM, репликация, бэкапы и витрины.",
    lessons: [
      {
        slug: "sql-queues",
        title: "Очереди на SQL",
        summary: "SELECT FOR UPDATE SKIP LOCKED забирает свободную строку. NOWAIT не ждёт чужую блокировку.",
      },
      {
        slug: "advisory-locks",
        title: "Advisory locks",
        summary: "Рекомендательная блокировка работает как распределённый мьютекс между сессиями.",
      },
      {
        slug: "orm",
        title: "ORM и SQLAlchemy",
        summary: "Сессия держит объекты. Lazy тянет связь отдельным запросом, eager — сразу. N+1 и границы транзакции.",
      },
      {
        slug: "migrations",
        title: "Миграции",
        summary: "Alembic меняет схему. Безопасный шаг не берёт длинную блокировку. ADD COLUMN с DEFAULT в новых версиях не переписывает таблицу.",
      },
      {
        slug: "replication",
        title: "Репликация",
        summary: "Физическая копирует страницы, логическая — строки. Слот удерживает WAL. Lag показывает отставание read-only реплики.",
      },
      {
        slug: "backup",
        title: "Бэкапы и PITR",
        summary: "pg_dump снимает логическую копию. pgBackRest и WAL-G возвращают кластер на момент по журналу.",
      },
      {
        slug: "monitoring",
        title: "Мониторинг и диагностика",
        summary: "pg_stat_statements, pg_stat_activity, wait events и блокировки показывают, кто и чего ждёт.",
      },
      {
        slug: "analytics-model",
        title: "Моделирование под аналитику",
        summary: "Звезда и снежинка: факты в центре, измерения вокруг.",
      },
      {
        slug: "etl",
        title: "ETL/ELT и витрины",
        summary: "Данные грузят в сырой слой, считают витрину и отдают её через semantic layer.",
      },
    ],
  },
];

export function trackPath(trackSlug: string): string {
  return `/learn/${trackSlug}`;
}

export function lessonPath(trackSlug: string, lessonSlug: string): string {
  return `/learn/${trackSlug}/${lessonSlug}`;
}

export function findTrack(trackSlug: string): Track | undefined {
  return tracks.find((track) => track.slug === trackSlug);
}

export function findLesson(
  trackSlug: string,
  lessonSlug: string,
): { track: Track; lesson: Lesson } | undefined {
  const track = findTrack(trackSlug);
  const lesson = track?.lessons.find((item) => item.slug === lessonSlug);
  if (!track || !lesson) return undefined;
  return { track, lesson };
}

export function lessonNeighbors(trackSlug: string, lessonSlug: string): {
  previous?: Lesson;
  next?: Lesson;
} {
  const track = findTrack(trackSlug);
  const index = track?.lessons.findIndex((item) => item.slug === lessonSlug) ?? -1;
  if (!track || index < 0) return {};
  return {
    previous: index > 0 ? track.lessons[index - 1] : undefined,
    next: index < track.lessons.length - 1 ? track.lessons[index + 1] : undefined,
  };
}

export function trackCrumb(match: {
  params?: Record<string, string | undefined>;
}): string | null {
  const slug = match.params?.track;
  if (!slug) return null;
  return findTrack(slug)?.title ?? null;
}

export function lessonCrumb(match: {
  params?: Record<string, string | undefined>;
}): string | null {
  const trackSlug = match.params?.track;
  const lessonSlug = match.params?.lesson;
  if (!trackSlug || !lessonSlug) return null;
  return findLesson(trackSlug, lessonSlug)?.lesson.title ?? null;
}

export function stepCount(count: number): string {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return `${count} шаг`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} шага`;
  return `${count} шагов`;
}

export function coursePaths(): string[] {
  return tracks.flatMap((track) => [
    trackPath(track.slug),
    ...track.lessons.map((lesson) => lessonPath(track.slug, lesson.slug)),
  ]);
}
