# AHS Admin Panel  
![Last Commit](https://img.shields.io/github/last-commit/dcx7c5/ahs-admin-panel.svg)  

![Django](https://img.shields.io/badge/Django-5.x-brightgreen?logo=django)  
![Node.js](https://img.shields.io/badge/Node.js-18.x-green?logo=node.js)  
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)  
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)  
![React](https://img.shields.io/badge/React-19.x-cyan?logo=react)  
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue?logo=typescript)  

---

## Project Overview  

The AHS Admin Panel is a modular and extendable framework built with Django and Node.js. It supports real-time communication, background task execution, collaborative workspaces, and more.  

The project is organized into **Core Modules**, **Plugins**, and **Custom Management Commands**, each fulfilling distinct roles.  

---

## Apps Breakdown  

### Core Modules  

The following essential Django apps serve as the foundation of the project:  

- **[ahs_api](backend/ahs_api)**: API layer of the project. Provides serialization, view layers, and HTTP endpoint handling.  
- **[ahs_channels](backend/ahs_channels)**: Implements real-time communication with WebSocket support.  
- **[ahs_core](backend/ahs_core)**: Contains core utilities, authentication features, cryptographic tools, and shared components.  
- **[ahs_endpoints](backend/ahs_endpoints)**: Handles API endpoints, including health checks for external integrations.  
- **[ahs_settings](backend/ahs_settings)**: Centralized application configuration and management of project settings.  
- **[ahs_network](backend/ahs_network)**: Manages network-related functionalities.  
  - **[domains](backend/ahs_network/domains)**: Handles domain management.  
  - **[hosts](backend/ahs_network/hosts)**: Manages host-related operations.  
  - **[ipaddresses](backend/ahs_network/ipaddresses)**: Handles IP address functionalities.  
- **[ahs_socket_conns](backend/ahs_socket_conns)**: Socket-based communication handling.  
- **[ahs_tasks](backend/ahs_tasks)**: Manages asynchronous tasks and background processes.  
- **[ahs_workers](backend/ahs_workers)**: Implements worker processes for distributed task execution.  

---

### Plugins / Apps  

These additional apps provide extended functionalities:  

- **[apps](backend/apps)**: Serves as a container for modular plugins.  
  - **[bookmarks](backend/apps/bookmarks)**: Adds bookmarking features for organizing user-specific content.  
  - **[osint](backend/apps/osint)**: Gathers Open Source Intelligence (OSINT) data from public sources.  
  - **[system](backend/apps/system)**: Involves system-level resource management:  
    - **[cpu](backend/apps/system/cpu)**: Tracks CPU usage and system performance.  
    - **[filesystem](backend/apps/system/filesystem)**: File system operations and health monitoring.  
    - **[docker](backend/apps/system/docker)**: Docker container monitoring and management.  
    - **[security](backend/apps/system/security)**: Tools related to auditing and improving system security.  
  - **[workspaces](backend/apps/workspaces)**: Provides collaborative workspace functionality for teams.  
  - **[xapi](backend/apps/xapi)**: Manages integrations with external APIs and services.  

---

## Custom Management Commands  

Below is a list of custom Django management commands included in the project:  

- **[ahs_core](backend/ahs_core)**:  
  - `ahs.py`: Entry point for various custom AHS-related tasks.  
  - `cleanmigrations.py`: Cleans up unused or redundant migration files.  
  - `compose.py`: Handles project composition logic.  
  - `firstsetup.py`: Automates the initial setup for the project.  
  - `migrations.py`: Runs customized migration-related tasks.  
  - `populate.py`: Populates the database with default or test data.  
  - `server.py`: Custom server-related tasks.  

- **[ahs_api](backend/ahs_api)**:  
  - `createrootkey.py`: Generates a new root key for authentication or encryption purposes.  

---

## Getting Started  

Follow the steps below to set up and run this project locally:  


### Secret Key Setup  

Generate a new secret key for the project and update the `SECRET_KEY` in the `.env` file:
   ```bash
   python -c 'import secrets; print(secrets.token_urlsafe(48))'  
   ```  

### SSL certificate and key setup

1. Create the certificate directory
   ```bash
   mkdir /path/to/project/.certs && cd /path/to/project/.certs/
   ```
2. Install the local CA in the system trust store.
   ```bash
   mkcert -install
   ```
3. Create the certificate and key
   ```bash
   mkcert -cert-file localhost.pem -key-file localhost-key.pem localhost 127.0.0.1
   ```


### SSL certificate and key setup

```bash
$ mkdir /path/to/project/.certs && cd /path/to/project/.certs/
$ mkcert -install   # Install the local CA in the system trust store.
$ mkcert -cert-file localhost.pem -key-file localhost-key.pem localhost 127.0.0.1
```

### Environment Configuration  

1. Rename `example.env` to `.env`.  
2. Populate the `.env` file with the required variables as shown below:  

| Variable            | Required | Description                                            |  
|---------------------|----------|--------------------------------------------------------|  
| `DEBUG`             | Yes      | Set `True` for development mode, or `False` for production. |  
| `SECRET_KEY`        | Yes      | A secure, randomly-generated key for Django.          |  
| `DB_USER`           | Yes      | Username for the PostgreSQL database.                 |  
| `DB_PASS`           | Yes      | Password for the PostgreSQL database.                 |  
| `DB_NAME`           | Yes      | Name of the PostgreSQL database.                      |  
| `DB_HOST`           | Optional | Leave blank for UNIX sockets or specify a host name.  |  

---
 
## Running the Project  

Once the environment is configured:  

1. Install dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  

2. Run migrations:  
   ```bash  
   python manage.py migrate  
   ```  

3. Start the development server:  
   ```bash  
   python manage.py runserver  
   ```  

---

## Additional Notes  

- Ensure that any new modules or apps are placed in appropriate directories to maintain organization and extensibility.  
- Contributors must test all changes and confirm proper functioning before pushing updates.  

---