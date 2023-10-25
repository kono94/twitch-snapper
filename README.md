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
cd database
docker compose up -d
```

MariaDB is running on port 3306
phpMyAdmin is running on port 8080

### Testing

```bash
cd database
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
