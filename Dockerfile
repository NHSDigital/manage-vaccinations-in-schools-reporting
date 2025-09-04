FROM python:3.13.7-alpine AS builder

WORKDIR /app

ADD package.json package-lock.json pyproject.toml uv.lock Makefile /app/

RUN apk add build-base libffi-dev npm bash curl

RUN pip install uv

ADD ./mavis/reporting /app/mavis/reporting
ADD README.md /app/

RUN uv sync --frozen --all-extras
RUN npm install

FROM builder

WORKDIR /app

RUN make build-assets

RUN addgroup --gid 1000 app
RUN adduser app -h /app -u 1000 -G app -DH
RUN mkdir -p /app/.cache/uv && chown -R app:app /app/.cache
RUN chown -R app:app /app/.venv

USER 1000

VOLUME ["/tmp", "/var/tmp", "/usr/tmp"]

# pass through additional arguments like --workers=5 via GUNICORN_CMD_ARGS
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "mavis.reporting:create_app()"]
