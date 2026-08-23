.PHONY: up down build logs seed migrate test clean

# Start all services
up:
	docker compose up --build -d

# Stop all services
down:
	docker compose down

# Rebuild all containers
build:
	docker compose build --no-cache

# View logs
logs:
	docker compose logs -f

# Run database migrations
migrate:
	docker compose exec backend alembic upgrade head

# Seed demo data
seed:
	docker compose exec backend python -m app.seed

# Run backend tests
test:
	docker compose exec backend pytest tests/ -v

# Reset everything (including database volume)
clean:
	docker compose down -v
	rm -rf pgdata

# Full setup: build, start, migrate, seed
setup: up
	@echo "Waiting for services to start..."
	@sleep 5
	@$(MAKE) migrate
	@$(MAKE) seed
	@echo ""
	@echo "================================================"
	@echo "  AgentCrashLab is running!"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo "================================================"
