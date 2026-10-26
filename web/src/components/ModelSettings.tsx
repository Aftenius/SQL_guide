import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import {
  ApiError,
  checkLearnerModel,
  clearLearnerModel,
  loadLearnerModel,
  saveLearnerModel,
} from "../api";
import { buttonClass, buttonQuietClass, fieldClass } from "./ui";

const providers = [
  {
    id: "deepseek",
    title: "DeepSeek",
    models: ["deepseek-chat", "deepseek-reasoner"],
  },
] as const;

export function ModelSettings() {
  const client = useQueryClient();
  const saved = useQuery({ queryKey: ["learner-model"], queryFn: loadLearnerModel });
  const [provider, setProvider] = useState("deepseek");
  const [model, setModel] = useState("deepseek-chat");
  const [apiKey, setApiKey] = useState("");
  const [notice, setNotice] = useState("");
  const chosen = providers.find((item) => item.id === provider) ?? providers[0];

  useEffect(() => {
    if (!saved.data?.provider || !saved.data.model) return;
    setProvider(saved.data.provider);
    setModel(saved.data.model);
  }, [saved.data]);

  const save = useMutation({
    mutationFn: () => saveLearnerModel(provider, model, apiKey),
    onSuccess: async (result) => {
      setApiKey("");
      setNotice(result.hint ? `Ключ сохранён, окончание ${result.hint}.` : "Модель сохранена.");
      await client.invalidateQueries({ queryKey: ["learner-model"] });
    },
  });
  const check = useMutation({
    mutationFn: () => checkLearnerModel(provider, model, apiKey),
    onSuccess: () => setNotice("DeepSeek принял ключ для этой модели."),
  });
  const clear = useMutation({
    mutationFn: clearLearnerModel,
    onSuccess: async () => {
      setApiKey("");
      setNotice("Ключ удалён.");
      await client.invalidateQueries({ queryKey: ["learner-model"] });
    },
  });
  const error = save.error ?? check.error ?? clear.error;

  return (
    <section className="sketch-box bg-white p-4">
      <h2 className="text-sm font-bold">Модель для обучения</h2>
      <p className="mt-2 max-w-2xl text-sm text-stone-700">
        Свой ключ DeepSeek нужен, когда обучение объясняет шаг. Ключ шифруется в аккаунте и
        больше не показывается. Проверка спрашивает у DeepSeek список моделей и не сохраняет ключ.
      </p>
      <form
        className="mt-4 grid gap-3 sm:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault();
          save.mutate();
        }}
      >
        <label className="grid gap-1 text-sm">
          Провайдер
          <select
            className={fieldClass}
            value={provider}
            onChange={(event) => {
              const next = event.target.value;
              setProvider(next);
              const first = providers.find((item) => item.id === next)?.models[0];
              if (first) setModel(first);
            }}
          >
            {providers.map((item) => (
              <option key={item.id} value={item.id}>
                {item.title}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm">
          Модель
          <select
            className={fieldClass}
            value={model}
            onChange={(event) => setModel(event.target.value)}
          >
            {chosen.models.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1 text-sm sm:col-span-2">
          Ключ API
          <input
            className={fieldClass}
            type="password"
            autoComplete="off"
            spellCheck={false}
            value={apiKey}
            placeholder={saved.data?.hint ? `сохранён ····${saved.data.hint}` : "sk-..."}
            onChange={(event) => setApiKey(event.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-2 sm:col-span-2">
          <button type="submit" className={buttonClass} disabled={save.isPending}>
            Сохранить
          </button>
          <button
            type="button"
            className={buttonQuietClass}
            disabled={check.isPending}
            onClick={() => check.mutate()}
          >
            Проверить
          </button>
          {saved.data?.configured ? (
            <button
              type="button"
              className={buttonQuietClass}
              disabled={clear.isPending}
              onClick={() => clear.mutate()}
            >
              Удалить ключ
            </button>
          ) : null}
        </div>
      </form>
      {notice ? <p className="mt-3 text-sm text-stone-700">{notice}</p> : null}
      {error instanceof ApiError ? <p className="mt-3 text-sm text-rose-800">{error.message}</p> : null}
      {saved.isError ? (
        <p className="mt-3 text-sm text-rose-800">Настройки модели не открылись.</p>
      ) : null}
    </section>
  );
}
