

DOCKER_IMAGE ?= mavis-reporting:latest
HOST_PORT ?= 5000
COVERAGE_THRESHOLD ?= 80

.PHONY: clean
clean:
	@rm -f sentinel
	@rm -rf node_modules
	@rm -rf .venv
	@rm -rf __pycache__

sentinel: package.json package-lock.json pyproject.toml uv.lock
	@echo "== Installing dependencies =="
	@npm install || (echo "Failed to install npm dependencies"; exit 1)
	@uv sync --all-extras || (echo "Failed to install Python dependencies"; exit 1)

	@echo "== Copying NHSUK favicons =="
	@make copy-nhsuk-favicons

	@touch sentinel

build-assets: sentinel
	@npm run build:scss
	@npm run build:js

.PHONY: install
install: sentinel

.PHONY: lint
lint: install
	uv run ruff check .

.PHONY: lint-fix
lint-fix: install
	uv run ruff check --fix .

.PHONY: dev
dev: install
	@echo "== Starting development servers =="
	@echo "Press Ctrl+C to stop all processes"
	@uv run honcho start -f Procfile.dev

.PHONY: copy-nhsuk-favicons
copy-nhsuk-favicons:
	mkdir -p mavis_reporting/static/favicons
	cp -r node_modules/nhsuk-frontend/dist/nhsuk/assets/images/* mavis_reporting/static/favicons/

build-docker:
	docker build -t ${DOCKER_IMAGE} .

.PHONY: run-docker
run-docker:
	docker run --rm -p ${HOST_PORT}:5000 -e GUNICORN_CMD_ARGS=${GUNICORN_CMD_ARGS} ${DOCKER_IMAGE}

test: install
	@echo "Running all tests .."
	@uv run pytest tests --verbose

.PHONY: test-coverage
test-coverage: install
	@echo "Checking coverage on all tests .."
	@uv run coverage run -m  pytest tests --verbose
	@uv run coverage report --fail-under=${COVERAGE_THRESHOLD}
	@uv run coverage html
	@uv run coverage xml coverage.xml
	@uv run coverage-badge -o coverage.svg
