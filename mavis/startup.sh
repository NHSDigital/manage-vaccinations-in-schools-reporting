#!/bin/sh
set -e

if [ "$HTTP_MODE" = "HTTPS" ]; then
openssl req -x509 -newkey rsa:4096 -nodes -out /tmp/cert.pem -keyout /tmp/key.pem -days 365 -subj '/CN=localhost'

# Start Gunicorn for HTTPS (port 443)
mise exec -- uv run --no-sync gunicorn \
  --bind 0.0.0.0:${PORT} \
  --keyfile=/tmp/key.pem \
  --certfile=/tmp/cert.pem \
  --http-protocols=h2 \
  --worker-class=gthread \
  --config /app/mavis/reporting/gunicorn.conf.py \
  'mavis.reporting:create_app()'
else
  mise exec -- uv run --no-sync gunicorn \
  --bind 0.0.0.0:${PORT} \
  'mavis.reporting:create_app()'
fi
