
install-uv:
	pip install --upgrade pip
	pip install uv

setup-env:
	@if [ -f .env ]; then \
		echo ".env already exists. Skipping..."; \
	else \
		cp .env.example .env; \
		echo "✓ Created .env from .env.example"; \
		echo "⚠️  Please review and update .env with your local values"; \
	fi

install:
	uv lock
	uv sync --group dev

add:
	@if [ -z "$(pkg)" ]; then \
		echo "Usage: make add pkg=<package_name>"; \
		exit 1; \
	fi
	uv add $(pkg)

build:
	docker compose build

up:
	docker compose up --build -d

down:
	docker compose down

restart: down up

migrate:
	docker compose exec app uv run alembic -c src/db/alembic.ini upgrade head

migrations:
	docker compose exec app uv run alembic -c src/db/alembic.ini revision --autogenerate -m "$(msg)"

test:
	PYTHONPATH=./src uv run pytest $(path)

fix:
	uv run ruff format .
	uv run ruff check --fix .

format:
	uv run ruff format .

lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src

pre-commit-install:
	uv run pre-commit install

.PHONY: install-uv install up down restart build add migrate migrations setup-env test fix format lint pre-commit-install
