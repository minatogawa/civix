.PHONY: help install dev build up down logs clean test lint format migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies in virtual environment"
	@echo "  dev         - Run development servers (bot + web)"
	@echo "  build       - Build Docker images"
	@echo "  up          - Start all services with Docker Compose"
	@echo "  down        - Stop all services"
	@echo "  logs        - Show logs from all services"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code with black"
	@echo "  migrate     - Run database migrations"
	@echo "  version     - Show current version"
	@echo "  release-*   - Create new release (patch/minor/major)"

# Development setup
install:
	python -m venv venv
	venv/Scripts/activate && pip install -r requirements.txt

# Run development servers
dev:
	@echo "Starting development servers..."
	@echo "Bot: python app/bot.py"
	@echo "Web: python app/app.py"
	@echo "Run these in separate terminals"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

# Development tools
test:
	venv/Scripts/activate && pytest tests/ -v

test-coverage:
	venv/Scripts/activate && pytest tests/ -v --cov=app --cov-report=html

# Linting
lint:
	venv/Scripts/activate && flake8 app/ tests/

lint-ruff:
	venv/Scripts/activate && ruff check app/ tests/

lint-all: lint lint-ruff

# Formatting
format:
	venv/Scripts/activate && black app/ tests/
	venv/Scripts/activate && isort app/ tests/

format-check:
	venv/Scripts/activate && black --check app/ tests/
	venv/Scripts/activate && isort --check-only app/ tests/

# Ruff format (alternative to black)
format-ruff:
	venv/Scripts/activate && ruff format app/ tests/

format-ruff-check:
	venv/Scripts/activate && ruff format --check app/ tests/

# Fix imports and formatting
fix:
	venv/Scripts/activate && ruff check --fix app/ tests/
	venv/Scripts/activate && black app/ tests/
	venv/Scripts/activate && isort app/ tests/

# CI pipeline commands
ci-test: lint-all format-check test

# Alternative CI with ruff only
ci-ruff: lint-ruff format-ruff-check test

# Pre-commit hooks
install-hooks:
	venv/Scripts/activate && pre-commit install

update-hooks:
	venv/Scripts/activate && pre-commit autoupdate

run-hooks:
	venv/Scripts/activate && pre-commit run --all-files

run-hooks-fast:
	venv/Scripts/activate && pre-commit run --all-files --hook-stage manual

# Development setup with hooks
setup-dev: install install-hooks
	@echo "Development environment ready!"
	@echo "Pre-commit hooks installed."
	@echo "Run 'make run-hooks' to test all hooks."

# Database
migrate:
	venv/Scripts/activate && flask db upgrade

seed:
	venv/Scripts/activate && python scripts/seed.py

backup:
	python scripts/backup.py create

restore:
	@echo "Available backups:"
	@python scripts/backup.py list
	@echo "Usage: make restore-file BACKUP=backup_file.sql"

restore-file:
	python scripts/backup.py restore data/postgres/$(BACKUP)

# Quick setup for new environment
setup: install
	cp .env.example .env
	@echo "Remember to configure .env with your actual values!"

# Version management
version:
	python scripts/release.py --current

version-info:
	python scripts/release.py --info

release-patch:
	python scripts/release.py patch

release-minor:
	python scripts/release.py minor

release-major:
	python scripts/release.py major

release-pre:
	@echo "Usage: make release-pre LEVEL=patch PRE=alpha"
	@echo "Example: make release-pre LEVEL=minor PRE=beta"
	python scripts/release.py $(LEVEL) --pre $(PRE)

# Production deployment
deploy:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
