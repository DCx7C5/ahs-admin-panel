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

MIGRATIONS_DIRS := $(shell find "$(PROJECT_DIR)/backend" -type d -name 'migrations')

NODE_MOD_DIR := $(shell find $(PROJECT_DIR) -type d -name 'node_modules')
WEBPACK_STATS := $(shell find $(PROJECT_DIR) -type f -name 'webpack-stats.json')

DOCKER_VOLS := $(shell docker volume ls --filter "name=^ahs" --format "{{.Name}}")
DOCKER_IMGS := $(shell docker images --filter "reference=ahs*" --format "{{.ID}}")
DOCKER_CONTS := $(shell docker ps -a --filter "name=^ahs" --format "{{.ID}}")
# FIX_BOOKMARKS := $(shell find $(PROJECT_DIR) -type f -name "bookmarks.json")
FIX_MENUITEMS := $(shell find $(PROJECT_DIR) -type f -name "menuitems.json")

DOCKER_NODE_CONT := $(shell  docker ps -a | grep "node" | cut -d' ' -f1 )

MODULES := accounts bookmarks core xapi


.ONESHELL:

.PHONY: setup clean install-py install-node migrate makemigrations createsuperuser \
		create_dirs set_permissions clean-migrations reset-migrations clean-sockets clean-node \
		clean-docker-volumes clean-docker-images clean-docker-containers docker-prune-all \
		docker-compose-start docker-compose-down create-super-user purge sleep

# Default target
setup: install-py docker-compose-start install-node makemigrations migrate create-super-user load-fixtures

purge: clean-sockets clean-node reset-migrations docker-compose-down \
       clean-docker-containers clean-docker-volumes clean-docker-images docker-prune-all

purge-reinit: purge setup

purge-reinit-venv: delete-venv purge-reinit

start: activate-venv
	@echo 'Virtual environment is active. Ready to work!'


activate-venv:
	@if [ ! -d "$(PROJECT_DIR)/.venv" ]; then \
		python -m venv .venv; \
	fi
	@echo ".venv is ready to use."

delete-venv:
	rm -rf "$(PROJECT_DIR)/.venv"
	@echo "Deleted python virtual env"

load-fixtures: activate-venv
	@echo 'Loading necessary database fixtures'
	$(PYTHON) manage.py loaddata "$(FIX_MENUITEMS)";
	# $(PYTHON) manage.py loaddata "$(FIX_BOOKMARKS)";
	@echo 'Done loading fixtures'

# Set permissions for the directories and socket files
set_permissions:
	@echo 'Setting permissions for socket directories...'
	chmod 775 "$(SOCKET_DIR_POSTGRES)" "$(SOCKET_DIR_REDIS)" "$(DOCKER_DIR)"
	chmod 770 "$(POSTGRES_SOCKET_FILE)"
	chmod 777 "$(REDIS_SOCKET_FILE)"
	@echo 'Permissions for socket dirs set.'


# Install Python dependencies
install-py: activate-venv
	@if [ -f "requirements.txt" ]; then \
		echo "Installing Python requirements..."; \
		$(PYTHON) -m pip install -r "requirements.txt" || { echo "Failed to install requirements"; exit 1; }; \
	else \
		echo "Requirements file not found. Skipping..."; \
	fi

# Install Node.js dependencies
install-node:
	docker container exec "ahs_node" npm install --save-dev
	@echo "Installed node/npm"



# Create new database migrations
makemigrations: activate-venv
	@echo 'Creating new database migrations...'
	$(PYTHON) manage.py makemigrations "$(MODULES)" || echo 'Makemigrations failed. Please ensure Django is set up correctly.'
	@echo 'Makemigrations completed.'

# Run database migrations
migrate: activate-venv
	@echo 'Running database migrations...'
	$(PYTHON) manage.py migrate "$(MODULES)" || echo 'Migrations failed. Please ensure Django is set up correctly.'
	@echo 'Database migrations completed.'

# Clean up socket directories, files, and dependencies
clean-sockets:
	@echo 'Cleaning up socket directories, files, and dependencies...'
	rm -f "$(POSTGRES_SOCKET_FILE)" "$(REDIS_SOCKET_FILE)"
	@echo 'Cleanup complete.'

# Clean migrations folders while preserving __init__.py
clean-migrations:
	@echo 'Cleaning migration files (preserving __init__.py)...'
	@for dir in $(MIGRATIONS_DIRS); do \
		find $$dir -type f ! -name '"__init__.py" -name "*.py"' -exec rm -f {} \;; \
		find $$dir -type f -name '*.pyc' -delete; \
		echo 'Cleaned migration files in $$dir'; \
	done
	@echo 'Migration cleanup complete.'

# Reset migrations by completely removing all migrations folders (EXERCISE CAUTION)
reset-migrations:
	@echo 'Resetting all migration folders...'
	@for dir in $(MIGRATIONS_DIRS); do \
		rm -rf $$dir; \
		echo 'Removed migrations folder: $$dir'; \
	done
	@echo 'Migration folder reset complete.'
	@echo 'Things'


clean-node:
	@echo 'Deleting all docker modules and webpack-stats.json'
	rm -rf $(NODE_MOD_DIR) && rm -f $(WEBPACK_STATS)
	@echo 'File and directory successfully deleted'


clean-docker-volumes:
	@echo 'Deleting all docker volumes - \(forces to reinit databases\)'
	@for vol in $(DOCKER_VOLS); do \
  		docker volume rm $$vol; \
		echo 'Removed docker volume: $$vol'; \
	done
	@echo 'Deleting docker volumes complete.'

clean-docker-images:
	@echo 'Deleting all docker images - \(forces to rebuild images\)'
	@for img in $(DOCKER_IMGS); do \
  		docker image rm $$img; \
		echo 'Removed docker image: $$img'; \
	done
	@echo 'Deleting docker images complete.'

clean-docker-containers:
	@echo 'Deleting all docker containers'
	@for cnt in $(DOCKER_CONTS); do \
  		docker container stop $$cnt && docker container rm $$cnt; \
		echo 'Removed docker container: $$cnt'; \
	done
	@echo 'Stopping/deleting docker containers complete.'

docker-prune-all:
	@echo 'Removing all stopped containers...'
	docker container prune -f
	@echo 'Remove unused local volumes'
	docker volume prune -f
	@echo 'Remove unused images'
	docker image prune -f
	@echo 'Everything pruned'

docker-compose-start:
	@echo 'Starting AHS docker compose service'
	docker compose -f "$(PROJECT_DIR)/docker-compose-dev.yaml" -p "ahs-admin-panel" up -d

docker-compose-stop:
	@echo 'Stopping AHS docker compose service'
	docker compose -f "$(PROJECT_DIR)/docker-compose-dev.yaml" -p "ahs-admin-panel" stop

docker-compose-down:
	@echo 'Stopping AHS docker compose service and removing containers'
	docker compose -f "$(PROJECT_DIR)/docker-compose-dev.yaml" -p "ahs-admin-panel" stop


create-super-user: activate-venv
	@echo 'Creating ahs-admin-panel superuser/root account'
	$(PYTHON) manage.py createsuperuser

