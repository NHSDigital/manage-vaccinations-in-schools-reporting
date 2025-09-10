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

## Runtime dependencies

This application authenticates with the main Mavis application using the [OAuth
2.0 Authorization Code
flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1).

Mavis should already have the development secrets set up in the development
environment. Make sure to turn on the `reporting_api` feature flag.

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
