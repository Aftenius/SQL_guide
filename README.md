# SQL_guide

Платформа ежедневной практики SQL и баз данных.

## Запуск API

```bash
uv sync --group dev
uv run sql-guide
```

Проверка жизни процесса: `GET http://127.0.0.1:8000/health`.

Миграции и учётки:

```bash
uv run alembic upgrade head
```

`POST /auth/register` и `POST /auth/login` создают аккаунт и корень прогресса. Вход выдаёт bearer-токен и refresh-cookie. `GET /me` возвращает сохранённый прогресс.

Вход через Яндекс ID использует тот же аккаунт: совпавший email привязывается, новый email создаёт учётку без пароля. В `.env` нужны `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` и `YANDEX_REDIRECT_URI`. Для интерфейса адрес возврата — `http://127.0.0.1:5173/login/yandex`. `GET /auth/yandex/start` возвращает адрес авторизации и ставит cookie `oauth_state`. `GET /auth/yandex/callback` проверяет state, обменивает code и выдаёт ту же сессию, что и вход по паролю.

## Интерфейс

```bash
cd web
npm install
npm run dev
```

Откройте `http://127.0.0.1:5173`. Vite проксирует `/auth`, `/me` и `/health` на API. У каждого шага свой адрес, например `/learn/sql/select`. Хлебные крошки собираются из этих сегментов.

## Сервер

На машине с Docker весь сайт открывается на одном порту:

```bash
docker compose up -d --build
```

Интерфейс и API: `http://<адрес-сервера>:2515`. Nginx отдаёт страницы и проксирует `/auth`, `/me` и `/health` в API. PostgreSQL наружу не публикуется. Перед первым запуском на чужом сервере задайте длинный `JWT_SECRET`. Если сайт открывается не с `127.0.0.1`, задайте `PUBLIC_ORIGIN`, например `http://203.0.113.10:2515`. Для HTTPS задайте ещё `COOKIE_SECURE=true`.

Локальная разработка по-прежнему может ходить в базу на `127.0.0.1:5433`:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres
```

Ученический SQL выполняется в отдельной базе `sql_guide_sandbox` от роли `sql_guide_sandbox`. На каждую попытку создаётся своя схема, запрос идёт с `statement_timeout`, затем транзакция откатывается. Роль не подключается к базе приложения. В проверку попадают только строки результата, не текст запроса.

