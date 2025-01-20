SHELL := /bin/sh

PROJECT_DIR := $(shell pwd)
PYTHON := .venv/bin/python
PIP := .venv/bin/pip

SOCKET_DIR_POSTGRES := $(PROJECT_DIR)/docker/postgres
SOCKET_DIR_REDIS := $(PROJECT_DIR)/docker/redis
DOCKER_DIR := $(PROJECT_DIR)/docker
POSTGRES_SOCKET_FILE := $(SOCKET_DIR_POSTGRES)/.s.PGSQL.5432
REDIS_SOCKET_FILE := $(SOCKET_DIR_REDIS)/redis.sock

SOCKET_USER := 999
SOCKET_GROUP := 1000
SOCKET_PERMS := 770

DOCKER_DIR_PERMS := 775
POSTGRES_DIR_PERMS := 775
REDIS_DIR_PERMS := 775

ENV_FILE := .env

PYTHON_REQUIREMENTS := requirements.txt
NODE_PACKAGE_JSON := frontend/package.json

MIGRATIONS_DIRS := $(shell find . -not \( -path ./.venv -prune \) -type d -name 'migrations')
APPS := $(shell find . -not \( -path ./.venv -prune \) -type d -name 'migrations' | cut -d"/" -f3)

NODE_MOD_DIR := $(shell find $(PROJECT_DIR) -type d -name 'node_modules')
WEBPACK_STATS := $(shell find $(PROJECT_DIR) -type f -name 'webpack-stats.json')

DOCKER_VOLS := $(shell docker volume ls --filter "name=^ahs" --format "{{.Name}}")
DOCKER_IMGS := $(shell docker images --filter "reference=ahs*" --format "{{.ID}}")
DOCKER_CONTS := $(shell docker ps -a --filter "name=^ahs" --format "{{.ID}}")
FIX_BOOKMARKS := $(shell find $(PROJECT_DIR) -type f -name "bookmarks.json")
FIXTURES := $(shell find $(PROJECT_DIR) -type f -name "fixtures.json")
DOCKER_NODE_CONT := $(shell  docker ps -a | grep "node" | cut -d' ' -f1 )
DOCKER_DB_VOL := $(shell docker volume ls | grep post | awk -F" " '{print $2}' )

MODULES := accounts bookmarks core xapi

.ONESHELL:

.PHONY: setup clean install-py install-node migrate makemigrations createsuperuser \
		create_dirs set_permissions clean-migrations reset-migrations clean-sockets clean-node \
		clean-docker-volumes clean-docker-images clean-docker-containers docker-prune-all \
		docker-compose-start docker-compose-down create-super-user purge sleep

# Default target
setup: activate-venv install-py docker-compose-start install-node makemigrations migrate create-super-user load-fixtures

purge: docker-compose-down clean-sockets clean-node reset-migrations \
       clean-docker-containers clean-docker-volumes clean-docker-images docker-prune-all

purge-reinit: purge setup

purge-reinit-venv: delete-venv purge-reinit


activate-venv:  # creates venv if not exists
	@if [ ! -d "$(PROJECT_DIR)/.venv" ]; then \
		python -m venv .venv; \
	fi
	@echo ".venv is ready to use."

delete-venv:  # delete whole .venv directory
	rm -rf "$(PROJECT_DIR)/.venv"
	@echo "Deleted python virtual env"

load-fixtures:  # loads on init necessary objects to db
	@echo 'Loading necessary database fixtures'
	$(PYTHON) manage.py loaddata "$(FIXTURES)";
	$(PYTHON) manage.py loaddata "$(FIX_BOOKMARKS)";
	@echo 'Done loading fixtures'

set_permissions:  # Set permissions for the directories and socket files
	@echo 'Setting permissions for socket directories...'
	chmod 775 "$(SOCKET_DIR_POSTGRES)" "$(SOCKET_DIR_REDIS)" "$(DOCKER_DIR)"
	chmod 770 "$(POSTGRES_SOCKET_FILE)"
	chmod 777 "$(REDIS_SOCKET_FILE)"
	@echo 'Permissions for socket dirs set.'

install-py:  # Install Python dependencies
	@if [ -f "requirements.txt" ]; then \
		echo "Installing Python requirements..."; \
		$(PYTHON) -m pip install -r "requirements.txt" || { echo "Failed to install requirements"; exit 1; }; \
	else \
		echo "Requirements file not found. Skipping..."; \
	fi

install-node:  # Install Node.js dependencies
	docker container exec "ahs_node" npm install --save-dev
	@echo "Installed node/npm"

makemigrations:  # Create new database migrations
	@echo 'Creating new database migrations...'
	@for da in $(APPS); do \
  		$(PYTHON) manage.py makemigrations $$da || echo 'Makemigration failed. Please ensure Django is set up correctly.'; \
  	done
	@echo 'Makemigrations completed.'

migrate:  # Run database migrations
	@echo 'Running database migrations...'
	@for da in $(APPS); do \
		$(PYTHON) manage.py migrate $$da || echo 'Migration failed. Please ensure Django is set up correctly.'; \
	done
	@echo 'Database migrations completed.'

clean-sockets:  # Clean up socket directories, files, and dependencies
	@echo 'Cleaning up socket directories, files, and dependencies...'
	rm -f "$(POSTGRES_SOCKET_FILE)" "$(REDIS_SOCKET_FILE)"
	@echo 'Cleanup complete.'

clean-migrations:  # Clean migrations folders while preserving __init__.py
	@echo 'Cleaning migration files (preserving __init__.py)...'
	@for dir in $(MIGRATIONS_DIRS); do \
		find $$dir -type f ! -name '"__init__.py" -name "*.py"' -exec rm -f {} \;; \
		find $$dir -type f -name '*.pyc' -delete; \
		echo 'Cleaned migration files in $$dir'; \
	done
	@echo 'Migration cleanup complete.'

reset-migrations:  # Reset migrations by completely removing all migrations folders (EXERCISE CAUTION)
	@echo 'Resetting all migration folders...'
	@for dir in $(MIGRATIONS_DIRS); do \
		rm -rf $$dir; \
		echo 'Removed migrations folder: $$dir'; \
	done
	@echo 'Migration folder reset complete.'
	@echo 'Things'

_clean-db-action:
	@echo 'Deleting complete Postgresql Database'
	docker volume rm "$(DOCKER_DB_VOL)"
	@echo 'Postgresql database deleted'



clean-db: docker-compose-down _clean-db-action docker-compose-start makemigrations migrate


clean-node:  # deletes npm and node container files
	@echo 'Deleting all docker modules and webpack-stats.json'
	rm -rf $(NODE_MOD_DIR) && rm -f $(WEBPACK_STATS)
	@echo 'File and directory successfully deleted'


clean-docker-volumes:  # delete docker project volumes (DB gets rebuild on django start)
	@echo 'Deleting all docker volumes'
	@for vol in $(DOCKER_VOLS); do \
  		docker volume rm $$vol; \
		echo 'Removed docker volume: $$vol'; \
	done
	@echo 'Deleting docker volumes complete.'

clean-docker-images:  # deletes docker project images (necessary when changes made in entrypoint.sh, dockerfile, etc., to rebuild with updated files)
	@echo 'Deleting all docker images'
	@for img in $(DOCKER_IMGS); do \
  		docker image rm $$img; \
		echo 'Removed docker image: $$img'; \
	done
	@echo 'Deleting docker images complete.'

clean-docker-containers:  # stops and removes all containers
	@echo 'Deleting all docker containers'
	@for cnt in $(DOCKER_CONTS); do \
  		docker container stop $$cnt && docker container rm $$cnt; \
		echo 'Removed docker container: $$cnt'; \
	done
	@echo 'Stopping/deleting docker containers complete.'

docker-prune-all:  # cleans all unused docker v,i,c's
	@echo 'Removing all stopped containers...'
	docker container prune -f
	@echo 'Remove unused local volumes'
	docker volume prune -f
	@echo 'Remove unused images'
	docker image prune -f
	@echo 'Everything pruned'

docker-compose-start:  # starts node,redis & postgres containers with compose
	@echo 'Starting AHS docker compose service'
	docker compose -f "$(PROJECT_DIR)/docker-compose-dev.yaml" -p "ahs-admin-panel" up -d

docker-compose-stop:  # stop the service
	@echo 'Stopping AHS docker compose service'
	docker compose -f "$(PROJECT_DIR)/docker-compose-dev.yaml" -p "ahs-admin-panel" stop

docker-compose-down:  # stops service and removes container
	@echo 'Stopping AHS docker compose service and removing containers'
	docker compose -f "$(PROJECT_DIR)/docker-compose-dev.yaml" -p "ahs-admin-panel" down

create-super-user:  # creates new superuser account for project
	@echo 'Creating ahs-admin-panel superuser/root account'
	$(PYTHON) manage.py createsuperuser
