COMPOSE_PROJECT_NAME_DEV=kedo_vpn_dev
COMPOSE_PROJECT_NAME_PROD=kedo_vpn_prod

COMPOSE_FILE_DEV = docker/docker-compose.dev.yaml
COMPOSE_FILE_PROD = docker/docker-compose.prod.yaml
ENV_FILE = .env

DC_DEV=docker compose -f $(COMPOSE_FILE_DEV) -p $(COMPOSE_PROJECT_NAME_DEV) --env-file $(ENV_FILE)
DC_PROD=docker compose -f $(COMPOSE_FILE_PROD) -p $(COMPOSE_PROJECT_NAME_PROD) --env-file $(ENV_FILE)

.PHONY: help \
dev-build dev-up dev-down dev-stop dev-restart dev-logs dev-shell \
dev-startapp dev-makemigrations dev-migrate dev-superuser dev-static \
prod-build prod-up prod-down prod-stop prod-restart prod-logs prod-shell \
prod-migrate prod-superuser prod-static

# ====================================================================================

dev-build:
	$(DC_DEV) build

dev-up:
	$(DC_DEV) up -d

dev-down:
	$(DC_DEV) down $(args)

dev-stop:
	$(DC_DEV) stop

dev-restart:
	$(DC_DEV) restart $(s)

dev-logs:
	$(DC_DEV) logs -f $(s)

dev-shell:
	$(DC_DEV) exec $(s) sh

dev-startapp:
	$(DC_DEV) exec backend python backend/manage.py startapp $(args)

dev-makemigrations:
	$(DC_DEV) exec backend python backend/manage.py makemigrations $(args)

dev-migrate:
	$(DC_DEV) exec backend python backend/manage.py migrate

dev-superuser:
	$(DC_DEV) exec backend python backend/manage.py createsuperuser

dev-static:
	$(DC_DEV) exec backend python backend/manage.py collectstatic --noinput

# ====================================================================================

prod-build:
	$(DC_PROD) build

prod-up:
	$(DC_PROD) up -d

prod-down:
	$(DC_PROD) down $(args)

prod-stop:
	$(DC_PROD) stop

prod-restart:
	$(DC_PROD) restart $(s)

prod-logs:
	$(DC_PROD) logs -f $(s)

prod-shell:
	$(DC_PROD) exec $(s) sh

prod-makemigrations:
	$(DC_DEV) exec backend python backend/manage.py makemigrations $(args)

prod-migrate:
	$(DC_PROD) exec backend python backend/manage.py migrate

prod-superuser:
	$(DC_PROD) exec backend python backend/manage.py createsuperuser

prod-static:
	$(DC_PROD) exec backend python backend/manage.py collectstatic --noinput
