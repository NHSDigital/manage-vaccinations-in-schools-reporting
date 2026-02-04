#!/bin/sh
set -e

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out /tmp/cert.pem -keyout /tmp/key.pem -days 365 -subj '/CN=localhost'

# Start Gunicorn with HTTPS
mise exec -- uv run --no-sync gunicorn \
  --bind 0.0.0.0:${PORT} \
  --keyfile=/tmp/key.pem \
  --certfile=/tmp/cert.pem \
  --http-protocols=h2,h1 \
  --worker-class=gthread \
  --config /app/mavis/reporting/gunicorn.conf.py \
  'mavis.reporting:create_app()'
  