import { z } from "zod";

const learnerSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  profile_created_at: z.string(),
});

const accessTokenSchema = z.object({
  access_token: z.string().min(1),
  token_type: z.string(),
});

const authorizationUrlSchema = z.object({
  authorization_url: z.string().url(),
});

const detailSchema = z.object({ detail: z.string() });

export type Learner = z.infer<typeof learnerSchema>;

const detailText: Record<string, string> = {
  "Email address is invalid": "Похоже, в адресе почты ошибка.",
  "Password must be at least 8 characters": "Пароль должен быть не короче 8 символов.",
  "Email is already registered": "Такая почта уже зарегистрирована.",
  "Invalid email or password": "Почта или пароль не подходят.",
  "Invalid or expired session": "Сессия истекла. Войдите ещё раз.",
  "Yandex sign-in could not be confirmed": "Яндекс не подтвердил вход. Начните ещё раз.",
  "Yandex sign-in failed": "Яндекс не завершил вход.",
  "Lesson key is invalid": "Такого шага нет.",
  "Unknown practice database": "Такой учебной базы нет.",
  "Practice tables could not be prepared": "Не удалось подготовить таблицы.",
  "Model choice is invalid": "Такой модели в списке нет.",
  "API key is invalid": "Ключ должен начинаться с sk- и быть длиннее.",
  "Saved API key cannot be read": "Сохранённый ключ не читается. Введите его ещё раз.",
  "Model API rejected the key": "Модель не приняла ключ. Проверьте его и попробуйте ещё раз.",
};

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function registerAccount(email: string, password: string): Promise<Learner> {
  return request("/auth/register", learnerSchema, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function loginAccount(email: string, password: string): Promise<Learner> {
  const token = await request("/auth/login", accessTokenSchema, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAccessToken(token.access_token);
  return request("/me", learnerSchema);
}

export async function refreshSession(): Promise<boolean> {
  try {
    const token = await request("/auth/refresh", accessTokenSchema, { method: "POST" });
    setAccessToken(token.access_token);
    return true;
  } catch (error) {
    setAccessToken(null);
    if (error instanceof ApiError && (error.status === 401 || error.status === 400)) {
      return false;
    }
    throw error;
  }
}

export async function logoutAccount(): Promise<void> {
  try {
    await request("/auth/logout", z.null(), { method: "POST" });
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;
  } finally {
    setAccessToken(null);
  }
}

export async function currentLearner(): Promise<Learner> {
  return request("/me", learnerSchema);
}

const practiceCalendarSchema = z.object({
  today: z.string(),
  streak: z.number().int(),
  days: z.array(z.object({ date: z.string(), solved: z.number().int() })),
  reviews: z.array(
    z.object({
      track: z.string(),
      lesson: z.string(),
      due_on: z.string(),
      interval_days: z.number().int(),
    }),
  ),
});

const solveResultSchema = z.object({
  track: z.string(),
  lesson: z.string(),
  due_on: z.string(),
  interval_days: z.number().int(),
  counted: z.boolean(),
  today: z.string(),
});

export type PracticeCalendar = z.infer<typeof practiceCalendarSchema>;
export type SolveResult = z.infer<typeof solveResultSchema>;

export async function loadPractice(): Promise<PracticeCalendar> {
  return request("/me/practice", practiceCalendarSchema);
}

const learnerModelSchema = z.object({
  configured: z.boolean(),
  provider: z.string().optional(),
  model: z.string().optional(),
  hint: z.string().optional(),
  updated_at: z.string().optional(),
});

export type LearnerModel = z.infer<typeof learnerModelSchema>;

export async function loadLearnerModel(): Promise<LearnerModel> {
  return request("/me/model", learnerModelSchema);
}

export async function saveLearnerModel(
  provider: string,
  model: string,
  apiKey: string,
): Promise<LearnerModel> {
  return request("/me/model", learnerModelSchema, {
    method: "PUT",
    body: JSON.stringify({ provider, model, api_key: apiKey }),
  });
}

export async function clearLearnerModel(): Promise<void> {
  await request("/me/model", z.null(), { method: "DELETE" });
}

export async function checkLearnerModel(
  provider: string,
  model: string,
  apiKey: string,
): Promise<void> {
  await request("/me/model/check", z.null(), {
    method: "POST",
    body: JSON.stringify({ provider, model, api_key: apiKey }),
  });
}

const queryResultSchema = z.object({
  columns: z.array(z.string()),
  rows: z.array(z.array(z.union([z.string(), z.number(), z.boolean(), z.null()]))),
  passed: z.array(z.number().int()),
});

export type QueryResult = z.infer<typeof queryResultSchema>;

export type QueryCheck = {
  sql: string;
  ordered: boolean;
  probe: string;
};

export async function runQuery(
  database: string,
  sql: string,
  checks: QueryCheck[],
): Promise<QueryResult> {
  return request("/query", queryResultSchema, {
    method: "POST",
    body: JSON.stringify({ database, sql, checks }),
  });
}

export async function recordSolve(track: string, lesson: string): Promise<SolveResult> {
  return request("/me/practice", solveResultSchema, {
    method: "POST",
    body: JSON.stringify({ track, lesson }),
  });
}

export async function yandexStart(): Promise<string> {
  const payload = await request("/auth/yandex/start", authorizationUrlSchema);
  return payload.authorization_url;
}

export async function yandexFinish(code: string, state: string): Promise<Learner> {
  const params = new URLSearchParams({ code, state });
  const token = await request(`/auth/yandex/callback?${params}`, accessTokenSchema);
  setAccessToken(token.access_token);
  return request("/me", learnerSchema);
}

async function request<T>(path: string, schema: z.ZodType<T>, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body) headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  let response: Response;
  try {
    response = await fetch(path, { ...init, headers, credentials: "include" });
  } catch {
    throw new ApiError("Не удалось связаться с сервером.", 0);
  }
  if (response.status === 204) return schema.parse(null);
  const payload: unknown = await readJson(response);
  if (!response.ok) {
    const message =
      response.status >= 500 ? "Сервер не сохранил данные. Попробуйте ещё раз." : explain(payload);
    throw new ApiError(message, response.status);
  }
  return schema.parse(payload);
}

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

function explain(payload: unknown): string {
  const parsed = detailSchema.safeParse(payload);
  if (!parsed.success) return "Запрос не выполнился.";
  return detailText[parsed.data.detail] ?? parsed.data.detail;
}
