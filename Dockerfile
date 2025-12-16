FROM python:3.14.2-alpine AS base
WORKDIR /app

ARG MISE_ENV=production
ENV MISE_ENV=${MISE_ENV} \
    MISE_CACHE_DIR=/tmp/.cache/mise \
    MISE_STATE_DIR=/tmp/.local/state/mise \
    MISE_TASK_RUN_AUTO_INSTALL=false \
    PATH="/root/.local/share/mise/shims:$PATH" \
    UV_CACHE_DIR=/tmp/.cache/uv

RUN apk add --no-cache mise sops uv

# Builder image
FROM base AS builder

RUN apk add --no-cache build-base libffi-dev bash npm

ADD mise.toml /app/
RUN mise trust

ADD package.json package-lock.json pyproject.toml uv.lock /app/
ADD mavis/reporting /app/mavis/reporting
RUN mise build

# Runtime image
FROM base

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/mavis /app/mavis
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

ADD config/credentials/*.enc.yaml /app/config/credentials/

# Don't copy mise.toml, only the environment-specific ones
ADD mise.*.toml /app/

RUN addgroup --gid 1000 app && \
    adduser app -h /app -u 1000 -G app -DH && \
    chown -R app:app /app

USER 1000
RUN mise trust --all

VOLUME ["/tmp", "/var/lib/amazon/ssm"]

ENV PORT=5000
CMD ["sh", "-c", "mise exec -- uv run --no-sync gunicorn --bind 0.0.0.0:${PORT} 'mavis.reporting:create_app()'"]
