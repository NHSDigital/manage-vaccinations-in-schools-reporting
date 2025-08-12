# Mavis Reporting

A Flask-based web application for the commissioner reporting component of Mavis.

## Prerequisites

- Mise
- Make

## Installation

1. **Install Mise**

   Please see the main Mavis repository for [how to install mise](https://github.com/nhsuk/manage-vaccinations-in-schools?tab=readme-ov-file#mise).

   Once mise is installed, run the following command to install the project dependencies:

   ```bash
   mise install
   ```

2. **Install project dependencies**

   This will install the project dependencies using Poetry and NPM.

   Note that the Poetry virtual environment will be created in the `.venv` directory to allow IDEs to use the correct Python interpreter.

   ```bash
   make install
   ```

3. **Create an environment file**

   Create a `.env` file in the root of the project following the example provided in `.env.example`.

4. **Run the application in development mode**

   ```bash
   make dev
   ```

   The application will be available at <http://localhost:5001>. 
   You will need a version of Mavis running which supports the OAuth 2.0 token authentication method - please see [Runtime Dependencies](#runtime-dependencies)  below for details.

## Linting

We use Ruff to lint the code. To run the linter, run the following command:

```bash
make lint
```

To run the linter with autofix, run the following command:

```bash
make lint-fix
```

To configure VSCode or variants thereof to use Ruff in your IDE, install the Ruff extension and it should be used automatically.

## Building & Running a Docker container

The application can be built and run via Docker, to support deployment to AWS. 
By default, the docker container listens on port 5000, but as Mac OS typically has an existing system application (Control Center) listening on port 5000, we use Docker's port mapping to map port 5001 on the host (your laptop) to 5000 on the container.

### Build

`make build-docker`

This will build a container image tagged with `mavis/reporting:latest`, which will listen on port 5000. To use a different tag, supply the `DOCKER_IMAGE` environment variable (e.g. `DOCKER_IMAGE=reporting-component:spike-11 make build-docker`)

Note that it will not push the image to any repository - you must do that manually if you want to.

### Run

`make run-docker`

This will run the container image tagged with `mavis/reporting:latest` and listen on the host port 5000.
To use a different tag, supply the `DOCKER_IMAGE` environment variable .
To map a different host port (for instance if you have something else running on port 5000) supply the `HOST_PORT` environment variable

Example:

`DOCKER_IMAGE=reporting-component:spike-11 HOST_PORT=5001 make run-docker` will run the container image tagged with `reporting-component:spike-11` and map port 5001 on the host to port 5000 on the container.

You could then access the running app with <http://localhost:5001> on your browser.

### Gunicorn arguments

Additional parameters to the `gunicorn` executable (for instance, the number of workers) can be passed through with the `GUNICORN_CMD_ARGS` environment variable.

Example:

```bash
% HOST_PORT=5555 GUNICORN_CMD_ARGS="--workers=5" make run-docker
docker run --rm -p 5555:5000 -e GUNICORN_CMD_ARGS=--workers=5 mavis-reporting:latest
[2025-07-17 10:32:01 +0000] [1] [INFO] Starting gunicorn 23.0.0
[2025-07-17 10:32:01 +0000] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
[2025-07-17 10:32:01 +0000] [1] [INFO] Using worker: sync
[2025-07-17 10:32:01 +0000] [10] [INFO] Booting worker with pid: 10
[2025-07-17 10:32:01 +0000] [11] [INFO] Booting worker with pid: 11
[2025-07-17 10:32:01 +0000] [12] [INFO] Booting worker with pid: 12
[2025-07-17 10:32:01 +0000] [13] [INFO] Booting worker with pid: 13
[2025-07-17 10:32:01 +0000] [14] [INFO] Booting worker with pid: 14
```

## Runtime dependencies

This application authenticates with the main Mavis application using the [OAuth 2.0 Authorization Code flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1).

To do this, it requires:

1. A copy of the main Mavis app must be running and available at the URL given in the `MAVIS_ROOT_URL` env var
2. That copy of Mavis must:
   - include [this corresponding PR](https://github.com/nhsuk/manage-vaccinations-in-schools/pull/3866/)
   - have the `reporting_api` feature flag enabled
   - have a value for `Settings.mavis_reporting_api.client_app.client_id` (..which can also be set via the `MAVIS_REPORTING_API__CLIENT_ID` environment variable) which matches this application's `CLIENT_ID` value
   - have a value for `Settings.mavis_reporting_api.client_app.client_secret` (..which can also be set via the `MAVIS_REPORTING_API__CLIENT_SECRET` environment variable) which matches this application's `CLIENT_SECRET` value
