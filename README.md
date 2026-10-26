# SQL_guide

Платформа ежедневной практики SQL и баз данных.

## Запуск API

```bash
uv sync --group dev
uv run uvicorn sql_guide.presentation.app:app --reload
```

Проверка жизни процесса: `GET http://127.0.0.1:8000/health`.

Миграции и учётки:

```bash
uv run alembic upgrade head
```

`POST /auth/register` и `POST /auth/login` создают аккаунт и корень прогресса. Вход выдаёт bearer-токен и refresh-cookie. `GET /me` возвращает сохранённый прогресс.

База приложения:

```bash
docker compose up -d postgres
```

