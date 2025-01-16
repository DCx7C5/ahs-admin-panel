# AHS

#### How to start:

<br>

##### Create new secret:
```bash
$ python -c 'import secrets;print(secrets.token_urlsafe(48))'

# Output:
<YOUR_SECRET_KEY>
```

<br>

##### Create .env file and save it in project root
```bash
# .env

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
- leave DB_HOST & DB_PORT empty to connect django & postgres container over a UNIX socket connection. 
- both containers mount the same volume which is mapped to UNIX socket parent dir
- IDE or Database Tool connects to postgresql DB on localhost:5433.

<br>

#### Start docker-compose 
```bash

docker compose \
  --env-file /path/to/adminpanel/.env \
  -f /path/to/adminpanel/docker-compose-dev.yaml \
  -p adminpanel up \
  -d \
  --build

```


#### Create django admin user 
```bash
# start a Terminal in django docker container and create adminpanel admin user

user@django:/project$ python manage.py createsuperuser

# Output:
Username: ...
Email Address: ...
...
```

<br>

###### Project is a admin user Cyber Management Suite, intended to run FAST on a desktop host. however... it will be fucking fast.

<br>
