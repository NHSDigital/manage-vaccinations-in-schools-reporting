FROM python:3.13.7-alpine AS builder
WORKDIR /app

ARG MISE_ENV=staging
ENV MISE_ENV=${MISE_ENV} PATH="/root/.local/share/mise/shims:$PATH"

RUN apk add --no-cache build-base libffi-dev mise

ADD mise*.toml /app/
ADD config/credentials/*.enc.yaml /app/config/credentials/
RUN mise install node python sops uv

ADD package.json package-lock.json pyproject.toml uv.lock /app/
ADD ./mavis/reporting /app/mavis/reporting
RUN mise build

FROM python:3.13.7-alpine
WORKDIR /app

ARG MISE_ENV=staging
ENV MISE_ENV=${MISE_ENV} PATH="/root/.local/share/mise/shims:$PATH"

COPY --from=builder /usr/bin/mise /usr/bin/mise
COPY --from=builder /root/.local/share/mise /root/.local/share/mise
COPY --from=builder /app /app

RUN addgroup --gid 1000 app && \
    adduser app -h /app -u 1000 -G app -DH && \
    chown -R app:app /app /root/.local/share/mise

USER 1000

EXPOSE 5000

CMD mise exec -- uv run gunicorn --bind 0.0.0.0:5000 mavis.reporting:create_app()
