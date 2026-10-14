.PHONY: help dev dev-backend dev-frontend test seed demo build up down clean

help:
	@echo "AuraCFO Command Reference:"
	@echo "  make dev          - Run both backend and frontend development servers"
	@echo "  make dev-backend  - Run FastAPI backend with Uvicorn"
	@echo "  make dev-frontend - Run Vite frontend server"
	@echo "  make test         - Run full pytest test suite"
	@echo "  make seed         - Seed Bengal Craft & Retail benchmark dataset"
	@echo "  make demo         - Run Deliverable 06 sandbox execution replay script"
	@echo "  make build        - Build Docker containers"
	@echo "  make up           - Start Docker Compose services"
	@echo "  make down         - Stop Docker Compose services"
	@echo "  make clean        - Remove caches, DB files, and build artifacts"

dev-backend:
	cd backend && python -m uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest tests/ -v

seed:
	cd backend && python -c "import asyncio; from app.services.benchmark_service import BenchmarkService; from app.dependencies import async_session_factory; asyncio.run(BenchmarkService.seed_scenario(async_session_factory, 'bengal_craft'))"

demo:
	cd backend && python -m tests.replay_sandbox

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -f backend/auracfo.db
