# Mavis Reporting

A Flask-based web application for the commissioner reporting component of Mavis.

## Installation

Please see the main Mavis repository for [how to install
mise](https://github.com/nhsuk/manage-vaccinations-in-schools?tab=readme-ov-file#mise).

```sh
mise install                               # Install dev tools
mise dev                                   # Run dev server
mise ci                                    # Run CI tests
```

The application will be available at <http://localhost:4001>.

You will need a version of Mavis running which supports the OAuth 2.0 token
authentication method - please see [Runtime Dependencies](#runtime-dependencies)
below for details.

## Other tasks

```sh
mise tasks # See all available tasks
mise env   # See all available environment variables
```

### Docker

To build and run the app in a Docker container, mimicking the production
environment:

```sh
mise docker
```

Different environment variables can be overwritten in `mise.local.toml`.

### Gunicorn arguments

Additional parameters to the `gunicorn` executable (for instance, the number of
workers) can be passed through with the `GUNICORN_CMD_ARGS` environment
variable.

Example:

```bash
% HOST_PORT=5555 GUNICORN_CMD_ARGS="--workers=5" mise docker:run
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

This application authenticates with the main Mavis application using the [OAuth
2.0 Authorization Code
flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1).

To do this, it requires:

1. A copy of the main Mavis app must be running and available at the URL given
   in the `MAVIS_ROOT_URL` env var
2. That copy of Mavis must:
   - have the `reporting_api` feature flag enabled
   - have a value for `Settings.reporting_api.client_app.client_id` (..which can
     also be set via the `MAVIS__REPORTING_API__CLIENT_APP__CLIENT_ID`
     environment variable) which matches this application's `CLIENT_ID` value
   - have a value for `Settings.reporting_api.client_app.secret` (..which can
     also be set via the `MAVIS__REPORTING_API__CLIENT_APP__SECRET` environment
     variable) which matches this application's `CLIENT_SECRET` value

## Secrets

This project uses encrypted secrets stored in `config/credentials`, using the
[mise secrets](https://mise.jdx.dev/environments/secrets.html) integration with
`age` and `sops`.

```sh
age-keygen -o config/credentials/staging.key           # Generate a new keypair
age-keygen -y config/credentials/staging.key           # View the public key

echo "FOO: bar" > config/credentials/staging.enc.yaml  # Create a secret file
sops encrypt -i --age $(age-keygen -y config/credentials/staging.key) \
  config/credentials/staging.enc.yaml                  # Encrypt the file
git add config/credentials/staging.enc.yaml            # It's now safe to commit

mise credentials:show                                  # Show secrets
mise credentials:edit                                  # Edit secrets
```
