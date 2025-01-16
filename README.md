# AHS Admin Panel 
![Last Commit](https://img.shields.io/github/last-commit/dcx7c5/ahs-admin-panel.svg)

![Django](https://img.shields.io/badge/Django-5.x-brightgreen?logo=django)
![Node.js](https://img.shields.io/badge/Node.js-18.x-green?logo=node.js)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)


---

### How to start:

###### Create new secret and update the SECRET_KEY env var in `.env`:
```bash
$ python -c 'import secrets;print(secrets.token_urlsafe(48))'

# Output:
<YOUR_SECRET_KEY>
```

<br>

---


#### Environment Configuration

###### Rename `example.env` to `.env` and configure it with your project environment variables. Below are all the variables and their purposes:

| Variable               | Required | Description                                                                 |
|------------------------|----------|-----------------------------------------------------------------------------|
| `DEBUG`               | Yes      | Set `True` for development mode, `False` for production.                    |
| `SECRET_KEY`          | Yes      | A randomly generated secret key for your Django app security.               |
| `DB_USER`             | Yes      | The PostgreSQL database username.                                           |
| `DB_PASS`             | Yes      | The PostgreSQL database password.                                           |
| `DB_NAME`             | Yes      | The name of the PostgreSQL database.                                        |
| `DB_HOST`             | Optional | Leave blank for UNIX socket, or specify host for external database.         |
| `DB_PORT`             | Optional | Leave blank for UNIX socket, or specify port for external database.         |
| `DJANGO_SETTINGS_MODULE` | Yes   | Set this variable to `adminpanel.settings`.                                 |
| `DB_BACKUP_ON_SHUTDOWN` | Optional | `1` to take a backup of DB on service shutdown, `0` to disable.             |
| `DB_RESTORE_ON_START` | Optional | `1` to restore DB backup on service start, `0` to disable.                  |

<br>

---

#### Example `.env` file:
```bash
DEBUG=True
SECRET_KEY=<YOUR_SECRET_KEY>
DB_USER=<YOUR_DB_USERNAME>
DB_PASS=<YOUR_DB_PASSWORD>
DB_NAME=ahs_dev
DB_HOST=
DB_PORT=
DJANGO_SETTINGS_MODULE='adminpanel.settings'
DB_BACKUP_ON_SHUTDOWN=1
DB_RESTORE_ON_START=0
```

###### -  leave DB_HOST & DB_PORT empty to connect django & postgres container over a UNIX socket connection. 
###### -  both containers mount the same volume which is mapped to UNIX socket parent dir
###### -  IDE or Database Tool connects to postgresql DB on localhost:5433.

<br>

---

#### Initial Setup via `makefile`:
```bash
  $ make setup
```
###

---

##### The `makefile` goes through the following steps:
- creates `.venv/` virtual environment for python 
- installs python and requirements
- starts ahs-admin-panel docker compose service
- installs npm and dependencies in ahs_node container
- makes migrations
- migrates
- creates superuser
- loads needed fixtures into DB

###

---




#### Run the development server
Start the local Django development server after completing the setup.

```bash
  $ python manage.py runserver
```

Access the server at [http://localhost:8000](http://localhost:8000).

---

#### Useful Docker Commands
- **Start services**: `docker compose -f docker-compose-dev.yaml -p ahs-admin-panel up -d`
- **Stop services**: `docker compose -f docker-compose-dev.yaml -p ahs-admin-panel down`
- **Stop services + remove containers**: `docker compose -f docker-compose-dev.yaml -p ahs-admin-panel down`
- **Restart Docker services**: `docker compose restart`


---


#### Makefile Commands

The project provides a `Makefile` to simplify common tasks. Below is a list of available commands:

| Command           | Description                                                                                       |
|-------------------|---------------------------------------------------------------------------------------------------|
| `make setup`      | Sets up the project by creating a Python virtual environment, installing dependencies, and starting services. |
| `make migrate`    | Runs database migrations for all Django apps.                                                    |
| `make makemigrations` | Generates database migrations for all Django apps.                                           |
| `make clean`      | Cleans up temporarily generated files like sockets and migrations.                               |
| `make purge`      | Stops services, removes containers, volumes, images, and cleans temp files.                      |
| `make load-fixtures` | Loads fixtures into the database (important for initial setup).                               |

Use these commands to streamline your local development workflow.

<br>

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)