DOCKER_COMPOSE_DEV=docker-compose.yml

build-dev:
	docker compose -f $(DOCKER_COMPOSE_DEV) build

build-dev-fe:
	docker compose -f $(DOCKER_COMPOSE_DEV) build frontend-tweenvest

build-dev-be:
	docker compose -f $(DOCKER_COMPOSE_DEV) build backend-tweenvest

start-dev:
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d  --force-recreate
	@echo "Frontend is running at http://127.0.0.1:3000"
	@echo "Backend is running at http://127.0.0.1:8080"
	@echo "     Open a new shell by running: make shell"
	@echo "     Create new migrations by running: make makemigrations"
	@echo "     Apply migrations by running: make migrate"

start-dev-build:
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d  --force-recreate --build

restart-dev:
	docker compose -f $(DOCKER_COMPOSE_DEV) restart

stop-dev:
	docker compose -f $(DOCKER_COMPOSE_DEV) down

migrate:
	$(MANAGE) migrate"

startapp:
	$(MANAGE) startapp $(APP_NAME)"

makemigrations:
	$(MANAGE) makemigrations"

showmigrations:
	$(MANAGE) showmigrations"
