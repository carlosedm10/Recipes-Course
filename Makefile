DOCKER_COMPOSE_DEV=docker-compose.yml
APP_CONTAINER=personal_projects-app
APP_DOCKER_EXEC_NO_TTI=docker exec $(APP_CONTAINER) bash -c

build:
	docker compose -f $(DOCKER_COMPOSE_DEV) build

start:
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d  --force-recreate
	@echo "Frontend is running at http://127.0.0.1:3000"
	@echo "Backend is running at http://127.0.0.1:8080"
	@echo "     Open a new shell by running: make shell"
	@echo "     Create new migrations by running: make makemigrations"
	@echo "     Apply migrations by running: make migrate"

start-build:
	docker compose -f $(DOCKER_COMPOSE_DEV) up -d  --force-recreate --build

restart:
	docker compose -f $(DOCKER_COMPOSE_DEV) restart

stop:
	docker compose -f $(DOCKER_COMPOSE_DEV) down

migrate:
	$(MANAGE) migrate"

.PHONY: app
app:
	docker-compose run --rm app sh -c "python manage.py startapp $(filter-out $@,$(MAKECMDGOALS))"

makemigrations:
	docker-compose run --rm app sh -c "python manage.py makemigrations"

showmigrations:
	$(MANAGE) showmigrations"

# format-all:
# 	$(APP_DOCKER_EXEC_NO_TTI) "python -m autoflake --exclude=node_modules/ --remove-all-unused-imports --in-place ./**/**/*.py"
# 	$(APP_DOCKER_EXEC_NO_TTI) "python -m isort --profile black -l 79 api/"
# 	$(APP_DOCKER_EXEC_NO_TTI) "python -m black --line-length 79 --preview api/"

run-tests:
	docker-compose run --rm app sh -c "python manage.py test"

create-superuser:
	docker-compose run --rm app sh -c "python manage.py createsuperuser"