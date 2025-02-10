# AHS Admin Panel 
![Last Commit](https://img.shields.io/github/last-commit/dcx7c5/ahs-admin-panel.svg)

![Django](https://img.shields.io/badge/Django-5.x-brightgreen?logo=django)
![Node.js](https://img.shields.io/badge/Node.js-18.x-green?logo=node.js)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)


---

# Project Overview: Apps Breakdown

This project contains various Django apps, divided into **Core Apps** and **Plugins**, that provide modular and extendable functionality.


## Core Modules 
These essential apps handle the foundational features of the project:

- **[ahs_crypto](backend/ahs_crypto)**: Handles cryptographic operations, including secure key generation and authentication.
- **[ahs_accounts](backend/ahs_accounts)**: Manages user accounts, profiles, and permissions for authentication.
- **[ahs_sessions](backend/ahs_sessions)**: Provides secure session management for user interactions.
- **[ahs_core](backend/ahs_core)**: Core utilities and shared functionalities across the project.
- **[ahs_channels](backend/ahs_channels)**: Implements real-time communications, such as WebSocket support.
- **[ahs_endpoints](backend/ahs_endpoints)**: Manages API definitions for interacting with external systems.
- **[ahs_settings](backend/ahs_settings)**: Central configuration management for application settings.
- **[ahs_socket_conns](backend/ahs_socket_conns)**: Handles socket-based connections for real-time interactions.
- **[ahs_tasks](backend/ahs_tasks)**: Manages background tasks and asynchronous job processing.
- **[ahs_workers](backend/ahs_workers)**: Worker processes for handling background tasks and distributed workloads.

---

## Plugins / Apps 
These apps provide additional features and extensibility:

- **[apps](backend/apps)**: A container app for modular plugins.
- **[bookmarks](backend/apps/bookmarks)**: Adds bookmarking functionality for user-specific content.
- **[network](backend/apps/network)**: Handles network-related functionality, such as monitoring and communication.
- **[osint](backend/apps/osint)**: Tools for Open Source Intelligence (OSINT), gathering data from public sources.
- **[system](backend/apps/system)**: A suite for managing system-level resources, with submodules:
  - [cpu](backend/apps/system/cpu): Monitors CPU resource usage.
  - [filesystem](backend/apps/system/filesystem): Handles filesystem operations and monitoring.
  - [docker](backend/apps/system/docker): Manages Docker containers and environments.
  - [security](backend/apps/system/security): Provides system security tools, such as audits.
- **[workspaces](backend/apps/workspaces)**: Implements collaborative user or team workspaces.
- **[xapi](backend/apps/xapi)**: Manages XAPI integrations for external connectivity.

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

| Variable                 | Required | Description                                                         |
|--------------------------|----------|---------------------------------------------------------------------|
| `DEBUG`                  | Yes      | Set `True` for development mode, `False` for production.            |
| `SECRET_KEY`             | Yes      | A randomly generated secret key for your Django app security.       |
| `DB_USER`                | Yes      | The PostgreSQL database username.                                   |
| `DB_PASS`                | Yes      | The PostgreSQL database password.                                   |
| `DB_NAME`                | Yes      | The name of the PostgreSQL database.                                |
| `DB_HOST`                | Optional | Leave blank for UNIX socket, or specify host for external database. |
| `DB_PORT`                | Optional | Leave blank for UNIX socket, or specify port for external database. |
| `DJANGO_SETTINGS_MODULE` | Yes      | Set this variable to `adminpanel.settings`.                         |
| `DB_BACKUP_ON_SHUTDOWN`  | Optional | `1` to take a backup of DB on service shutdown, `0` to disable.     |
| `DB_RESTORE_ON_START`    | Optional | `1` to restore DB backup on service start, `0` to disable.          |

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
DJANGO_SETTINGS_MODULE='adminpanel.ahs_settings'
DB_BACKUP_ON_SHUTDOWN=1
DB_RESTORE_ON_START=0
```

###### -  leave DB_HOST & DB_PORT empty to connect django & postgres container over a UNIX socket connection. 
###### -  both containers mount the same volume which is mapped to UNIX socket parent dir
###### -  IDE or Database Tool connects to postgresql DB on localhost:5433.

<br>

---

# **Makefile Overview**

This project includes a `Makefile` to simplify and automate common development tasks. It provides easy-to-use commands for setting up the development environment, managing dependencies, cleaning files, and working with Docker. Below is an overview of its primary use cases and key commands.

---

#### Run the development server
Start the local Django development server after completing the setup.

```bash
  $ python manage.py runserver
```

Access the server at [http://localhost:8000](http://localhost:8000).

---

