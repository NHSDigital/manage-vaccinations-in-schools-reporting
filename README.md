# Mavis Reporting

A Flask-based web application for the commissioner reporting component of Mavis.

## Installation

Please see the main Mavis repository for [how to install
mise](https://github.com/nhsuk/manage-vaccinations-in-schools?tab=readme-ov-file#mise).

```sh
mise dev                                   # Run dev server
mise ci                                    # Run CI tests
```

The application will be available at <http://localhost:4001>.

You will need a version of Mavis running which supports the OAuth 2.0 token
authentication method - please see [Runtime Dependencies](#runtime-dependencies)
below for details.

## Other tasks

```sh
mise tasks                                 # See all available tasks
mise env --env development                 # See env vars and dev secrets
```

### Docker

To build and run the app in a Docker container, mimicking the production
environment:

```sh
mise docker
```

Different environment variables can be overwritten in `mise.local.toml`.

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

mise credentials:show --env staging                    # Show secrets
mise credentials:edit --env staging                    # Edit secrets
```

To view and edit staging/production secrets, you need to obtain the
`config/credentials/staging.key` (or `production.key`) from a colleague.
