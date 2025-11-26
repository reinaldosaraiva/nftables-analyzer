.PHONY: help dev dev-backend dev-frontend build test lint clean install local local-backend local-frontend

help:
	@echo "Available commands:"
	@echo ""
	@echo "  Docker (recommended):"
	@echo "    make dev              - Start both backend and frontend in Docker (dev mode)"
	@echo "    make dev-backend      - Start only backend in Docker with hot reload"
	@echo "    make dev-frontend     - Start only frontend in Docker with hot reload"
	@echo "    make build            - Build production Docker images"
	@echo "    make clean            - Stop all containers and clean volumes"
	@echo ""
	@echo "  Local Development:"
	@echo "    make install          - Install all dependencies (backend + frontend)"
	@echo "    make local            - Start both services locally (requires 2 terminals)"
	@echo "    make local-backend    - Start backend locally (port 8000)"
	@echo "    make local-frontend   - Start frontend locally (port 3000)"
	@echo ""
	@echo "  Testing & Quality:"
	@echo "    make test             - Run all tests"
	@echo "    make lint             - Run linters"

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-backend:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build backend

dev-frontend:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build frontend

build:
	docker-compose build --no-cache

test:
	@echo "Running backend tests..."
	cd backend && uv run pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

lint:
	@echo "Linting backend..."
	cd backend && uv run ruff check src/
	cd backend && uv run mypy src/
	@echo "Linting frontend..."
	cd frontend && npm run lint

clean:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache
	rm -rf frontend/.next frontend/node_modules

# Local Development Commands
install:
	@echo "Installing backend dependencies..."
	cd backend && uv sync
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done! Run 'make local-backend' and 'make local-frontend' in separate terminals."

local-backend:
	cd backend && uv run uvicorn nftables_analyzer.api.main:app --host 0.0.0.0 --port 8000 --reload

local-frontend:
	cd frontend && npm run dev

local:
	@echo "Starting both services..."
	@echo "Run 'make local-backend' in one terminal and 'make local-frontend' in another."
	@echo "Or use: make dev (Docker)"
