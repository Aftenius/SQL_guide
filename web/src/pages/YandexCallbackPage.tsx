import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";

import { ApiError, yandexFinish } from "../api";
import { useRememberLearner } from "../session";
import { usePageTitle } from "../title";

export function YandexCallbackPage() {
  usePageTitle("Вход через Яндекс");
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const remember = useRememberLearner();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = params.get("code");
    const state = params.get("state");
    if (!code || !state) {
      setError("Яндекс не вернул данные для входа.");
      return;
    }
    let active = true;
    void yandexFinish(code, state)
      .then((learner) => {
        if (!active) return;
        remember(learner);
        void navigate("/learn", { replace: true });
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setError(caught instanceof ApiError ? caught.message : "Яндекс не завершил вход.");
      });
    return () => {
      active = false;
    };
  }, [navigate, params, remember]);

  return (
    <section className="max-w-xl">
      <h1 className="text-3xl font-bold">Вход через Яндекс</h1>
      {error ? (
        <>
          <p role="alert" className="mt-4 text-danger">
            {error}
          </p>
          <Link to="/login" className="mt-4 inline-flex min-h-11 items-center text-indigo-700">
            Вернуться ко входу
          </Link>
        </>
      ) : (
        <p className="mt-4 text-base text-stone-600">Подтверждаем вход и открываем курс.</p>
      )}
    </section>
  );
}
