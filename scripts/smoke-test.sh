#!/usr/bin/env sh
set -eu

suite="${1:-baseline}"

case "$suite" in
  baseline)
    targets="django:8101 fastapi:8102 django-bolt:8103 go-echo:8104 rust-axum:8105 php:8106 node:8107 java:8108 express:8109 fastify:8110 csharp:8111 cpp:8112"
    ;;
  variants)
    targets="django-uwsgi:8113 django-waitress:8114 django-gunicorn4:8116 django-uvicorn4:8117 django-gunicorn2:8118 django-gunicorn-gthread:8119 django-uvicorn1-asyncio:8120 django-uvicorn4-optimized:8121 go-echo4:8122 rust-axum4:8123 java4:8124 cpp4:8125"
    ;;
  all)
    targets="django:8101 fastapi:8102 django-bolt:8103 go-echo:8104 rust-axum:8105 php:8106 node:8107 java:8108 express:8109 fastify:8110 csharp:8111 cpp:8112 django-uwsgi:8113 django-waitress:8114 django-gunicorn4:8116 django-uvicorn4:8117 django-gunicorn2:8118 django-gunicorn-gthread:8119 django-uvicorn1-asyncio:8120 django-uvicorn4-optimized:8121 go-echo4:8122 rust-axum4:8123 java4:8124 cpp4:8125"
    ;;
  *)
    echo "usage: $0 {baseline|variants|all}" >&2
    exit 2
    ;;
esac

failures=0
for target in $targets; do
  name=${target%:*}
  port=${target##*:}
  if body=$(curl --fail --silent --show-error --max-time 5 "http://127.0.0.1:${port}/") \
    && printf '%s' "$body" | grep -Eq '"message"[[:space:]]*:[[:space:]]*"hello"'; then
    printf 'OK   %-28s %s\n' "$name" "$body"
  else
    printf 'FAIL %-28s port=%s\n' "$name" "$port"
    failures=$((failures + 1))
  fi
done

if [ "$failures" -ne 0 ]; then
  echo "Smoke test failed: $failures service(s)" >&2
  exit 1
fi

echo "Smoke test passed: $suite"
