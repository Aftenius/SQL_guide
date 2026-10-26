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

Вход через Яндекс ID использует тот же аккаунт: совпавший email привязывается, новый email создаёт учётку без пароля. В `.env` нужны `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` и `YANDEX_REDIRECT_URI`. `GET /auth/yandex/start` возвращает адрес авторизации и ставит cookie `oauth_state`. `GET /auth/yandex/callback` проверяет state, обменивает code и выдаёт ту же сессию, что и вход по паролю.

База приложения:

```bash
docker compose up -d postgres
```

