COMPOSE := docker compose
WEB := web

.PHONY: help build up down restart logs ps shell dbshell migrate makemigrations superuser collectstatic test clean

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

attach:
	$(COMPOSE) up

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

shell:
	$(COMPOSE) exec $(WEB) sh

dbshell:
	$(COMPOSE) exec db psql -U django_user -d django_db

migrate:
	$(COMPOSE) exec $(WEB) python manage.py migrate

makemigrations:
	$(COMPOSE) exec $(WEB) python manage.py makemigrations

superuser:
	$(COMPOSE) exec $(WEB) python manage.py createsuperuser

collectstatic:
	$(COMPOSE) exec $(WEB) python manage.py collectstatic --noinput

test:
	$(COMPOSE) exec $(WEB) python manage.py test

clean:
	$(COMPOSE) down -v --remove-orphans
