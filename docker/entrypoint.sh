#!/bin/sh
set -eu

cd /app

attempt=0
until alembic upgrade head; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "База не приняла миграции" >&2
    exit 1
  fi
  sleep 2
done

uvicorn sql_guide.presentation.app:app \
  --host 127.0.0.1 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips 127.0.0.1 &
api_pid=$!

nginx -g "daemon off;" &
web_pid=$!

trap 'kill "$api_pid" "$web_pid" 2>/dev/null || true' INT TERM

while kill -0 "$api_pid" 2>/dev/null && kill -0 "$web_pid" 2>/dev/null; do
  sleep 1
done

exit 1
