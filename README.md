## Twitch Snapper

```bash
sudo apt install python3.11-distutils
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

```bash
pipenv install
pipenv shell
python -m snapper.main
# just serve frontend
python -m snapper.main no_serve
```

```bash
docker compose -f docker-compose.dev.yaml up -d
```

MariaDB is running on port 3306
phpMyAdmin is running on port 8080

### Testing

```bash
docker compose -f docker-compose.test.yaml up -d
python -m unittest test.triggerTest
```

This will start a dev MariaDB database on port 3307 with test credentials.
The test script will load the default `.env` file and then override existing keys
like `APP_ENV` and `DATABASE_URI` from the `.env.test` file.

### Alembic

```bash
alembic init -t async alembic
```

Empty database, save the first revision:

```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply Migration:

```bash
alembic upgrade head
```

### Deployment Strategy

We utilize GitOps (as Dirk calls it) to deploy on the remote server. The deployment is kicked of when a new tag is pushed to the git repository. The Github Action Ci pipeline will just call the `deployment/update_via_ci.sh` script in the repo, everything will be built on the remote server. Hence, the process will look like this:

First, on the remote server, we have to `git clone` this repository and place the `age` private key in the `deployment/` folder. Then, for every tag pushed to this repository, the `deployment/update_via_ci.sh` is called from within the github pipeline on the remote server via ssh (a private ssh key is stored in the secrets on github for the `snapper` user that just has the permissions to call this specific script via the setuid-bit). The first argument for the script is the current tag, extracted by the pipeline. This tag is also used to build a docker container for the application. Additionally, `age` will decrypt the secrets for the `docker.env` and `.env.compose` which includes all secrets for the database and twitchAPI. Finally, `docker compose up -d` restarts the whole application.

#### Encrypt

```bash
cat deployment/docker.env | age -r age1r55yqzcf0qahgn54g3n6y7wncqxx9d80f024l3ck4kn36adw8gfspcnp4e | base64 > deployment/docker.env.encrypted
```

#### Decrypt

```bash
cat deployment/.env.compose.encrypted | base64 -d | age --decrypt -i key.txt > deployment/.env.compose
```
