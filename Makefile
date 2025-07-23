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

lint:
	venv/Scripts/activate && flake8 app/ tests/

format:
	venv/Scripts/activate && black app/ tests/

# Database
migrate:
	venv/Scripts/activate && flask db upgrade

# Quick setup for new environment
setup: install
	cp .env.example .env
	@echo "Remember to configure .env with your actual values!"

# Production deployment
deploy:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d