FROM python:3.13.7-alpine AS base
WORKDIR /app

ARG MISE_ENV=staging
ENV MISE_ENV=${MISE_ENV} \
    MISE_TASK_RUN_AUTO_INSTALL=false \
    PATH="/root/.local/share/mise/shims:$PATH"

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
ADD mise.*.toml /app/

RUN addgroup --gid 1000 app && \
    adduser app -h /app -u 1000 -G app -DH && \
    chown -R app:app /app

USER 1000
RUN mise trust --all

EXPOSE 5000
CMD ["mise", "exec", "--", "uv", "run", "--no-sync", "gunicorn", \
    "--bind", "0.0.0.0:5000", "mavis.reporting:create_app()"]
