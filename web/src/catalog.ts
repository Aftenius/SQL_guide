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
    slug: "sql",
    title: "SQL",
    summary: "От одной выборки к соединениям, изменениям и схеме.",
    lessons: [
      {
        slug: "select",
        title: "Выборка",
        summary: "SELECT читает столбцы из строк, которые уже лежат в таблице.",
      },
      {
        slug: "constraints",
        title: "Ограничения",
        summary: "Ключ, уникальность и NOT NULL держат в таблице допустимые строки.",
      },
      {
        slug: "filter-sort",
        title: "Фильтр и порядок",
        summary: "WHERE оставляет нужные строки, ORDER BY задаёт их порядок.",
      },
      {
        slug: "review",
        title: "Повторение",
        summary: "Короткий проход по выборке, фильтру и сортировке на одной задаче.",
      },
      {
        slug: "joins",
        title: "Соединения",
        summary:
          "INNER и внешние соединения складывают строки. Лишнее совпадение размножает результат.",
      },
      {
        slug: "nulls",
        title: "NULL",
        summary: "NULL — это отсутствие значения. Сравнение с ним не даёт истину.",
      },
      {
        slug: "expressions",
        title: "Выражения",
        summary: "В списке выборки можно посчитать новое значение из столбцов строки.",
      },
      {
        slug: "aggregates",
        title: "Агрегаты",
        summary: "COUNT и SUM сворачивают группу строк в одну.",
      },
      {
        slug: "execution-order",
        title: "Порядок выполнения",
        summary:
          "Запрос идёт FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT.",
      },
      {
        slug: "writes",
        title: "Изменение строк",
        summary: "INSERT, UPDATE и DELETE меняют строки, а RETURNING показывает результат.",
      },
      {
        slug: "schema",
        title: "Схема",
        summary: "CREATE, ALTER и DROP описывают, какие таблицы вообще существуют.",
      },
      {
        slug: "subqueries",
        title: "Подзапросы",
        summary: "Вложенный запрос отдаёт значение или набор, которым пользуется внешний.",
      },
      {
        slug: "set-operations",
        title: "Множества",
        summary: "UNION, INTERSECT и EXCEPT соединяют результаты по строкам, а не по столбцам.",
      },
      {
        slug: "case-dates",
        title: "CASE и даты",
        summary: "CASE выбирает ветку, а функции даты приводят время к одному виду.",
      },
      {
        slug: "cte-windows",
        title: "CTE и окна",
        summary: "CTE именует промежуточный результат, окно считает значение без свёртки строк.",
      },
      {
        slug: "one-row-per-customer",
        title: "Одна строка на клиента",
        summary: "Нужно оставить одну строку на клиента, не потеряв его заказы по дороге.",
      },
    ],
  },
  {
    slug: "patterns",
    title: "Паттерны",
    summary: "Как запрос выглядит правильно и где он тихо ломает результат.",
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
    ],
  },
  {
    slug: "scaling",
    title: "Масштабирование",
    summary: "Семь способов ускорить чтение, когда строк становится много.",
    lessons: [
      { slug: "indexes", title: "Индексы", summary: "Индекс сокращает поиск, если условие ему подходит." },
      {
        slug: "materialized-views",
        title: "Материализованные представления",
        summary: "Тяжёлый запрос сохраняют как таблицу и обновляют по расписанию.",
      },
      {
        slug: "denormalization",
        title: "Денормализация",
        summary: "Копию данных кладут рядом, чтобы не собирать её соединением на каждое чтение.",
      },
      {
        slug: "vertical-scaling",
        title: "Вертикальное масштабирование",
        summary: "Тот же сервер получает больше памяти и процессора.",
      },
      {
        slug: "caching",
        title: "Кэширование",
        summary: "Повторный ответ отдают из памяти, пока данные не устарели.",
      },
      {
        slug: "replication",
        title: "Репликация",
        summary: "Копии базы забирают чтение и остаются на случай отказа основной.",
      },
      {
        slug: "sharding",
        title: "Шардирование",
        summary: "Строки делят между несколькими базами по ключу.",
      },
    ],
  },
  {
    slug: "architecture",
    title: "Архитектура",
    summary: "Что обещать, когда база отказывает, и как вернуть её в строй.",
    lessons: [
      {
        slug: "rpo-rto",
        title: "RPO и RTO",
        summary: "RPO — сколько данных можно потерять, RTO — сколько длится простой.",
      },
      {
        slug: "backup",
        title: "Резервные копии",
        summary: "Копия и журнал позволяют восстановить базу на момент до сбоя.",
      },
      {
        slug: "failover",
        title: "Переключение",
        summary: "При отказе основной базы чтение и запись переходят на запасную.",
      },
      {
        slug: "split-brain",
        title: "Split brain",
        summary: "Две базы считают себя главными, если кворум не решил, кто пишет.",
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
