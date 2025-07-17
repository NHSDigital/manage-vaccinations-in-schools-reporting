FROM python:3.13-alpine AS builder

WORKDIR /app

ADD package.json package-lock.json pyproject.toml poetry.lock Makefile /app/

RUN apk add build-base libffi-dev npm

RUN pip install poetry
RUN make install


FROM builder 
WORKDIR /app

COPY --from=builder /app /app
ADD . /app

# Create a new group `app` with Group ID `1000`.
RUN addgroup --gid 1000 app
# Create a new user `app`, sets home directory to `/app`, User ID `1000`, in
# the group `app`. The `-DH` option results in a system account.
RUN adduser app -h /app -u 1000 -G app -DH
# Change the user for subsequent commands in Dockerfile to the user with ID
# `1000`.
USER 1000

CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:5000", "mavis_reporting:create_app()"]