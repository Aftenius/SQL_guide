import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { z } from "zod";

import { ApiError, loginAccount, registerAccount, yandexStart } from "../api";
import { buttonClass, buttonQuietClass, cardClass, fieldClass } from "../components/ui";
import { safeNext } from "../navigation";
import { useRememberLearner } from "../session";
import { usePageTitle } from "../title";

const credentialsSchema = z.object({
  email: z.string().trim().email("Похоже, в адресе почты ошибка."),
  password: z.string().min(8, "Пароль должен быть не короче 8 символов."),
});

export function LoginPage() {
  return <AuthForm mode="login" />;
}

export function RegisterPage() {
  return <AuthForm mode="register" />;
}

function AuthForm({ mode }: { mode: "login" | "register" }) {
  const isLogin = mode === "login";
  const title = isLogin ? "Вход" : "Регистрация";
  usePageTitle(title);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const remember = useRememberLearner();
  const next = safeNext(params.get("next"));
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsed = credentialsSchema.safeParse({ email, password });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Проверьте почту и пароль.");
      return;
    }
    setPending(true);
    setError(null);
    try {
      if (!isLogin) await registerAccount(parsed.data.email, parsed.data.password);
      const learner = await loginAccount(parsed.data.email, parsed.data.password);
      remember(learner);
      await navigate(next);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Запрос не выполнился.");
    } finally {
      setPending(false);
    }
  }

  async function startYandex() {
    setPending(true);
    setError(null);
    try {
      window.location.assign(await yandexStart());
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Запрос не выполнился.");
      setPending(false);
    }
  }

  return (
    <section className={`${cardClass} mx-auto max-w-md`}>
      <h1 className="font-serif text-3xl">{title}</h1>
      <p className="mt-2 text-muted">Аккаунт хранит прогресс по тем же адресам уроков.</p>
      <form className="mt-6 grid gap-4" onSubmit={(event) => void onSubmit(event)} noValidate>
        <label className="grid gap-1 text-sm font-medium">
          Почта
          <input
            className={fieldClass}
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>
        <label className="grid gap-1 text-sm font-medium">
          Пароль
          <input
            className={fieldClass}
            type="password"
            autoComplete={isLogin ? "current-password" : "new-password"}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            required
          />
        </label>
        {error ? (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        ) : null}
        <button className={buttonClass} type="submit" disabled={pending}>
          {isLogin ? "Войти" : "Создать аккаунт"}
        </button>
      </form>
      {isLogin ? (
        <button
          className={`${buttonQuietClass} mt-3 w-full`}
          type="button"
          disabled={pending}
          onClick={() => void startYandex()}
        >
          Войти через Яндекс ID
        </button>
      ) : null}
      <p className="mt-4 text-sm text-muted">
        {isLogin ? (
          <Link to={`/register?next=${encodeURIComponent(next)}`} className="text-moss">
            Создать аккаунт
          </Link>
        ) : (
          <Link to={`/login?next=${encodeURIComponent(next)}`} className="text-moss">
            У меня уже есть аккаунт
          </Link>
        )}
      </p>
    </section>
  );
}
