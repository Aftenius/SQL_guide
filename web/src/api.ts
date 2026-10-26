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
