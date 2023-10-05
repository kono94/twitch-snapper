## Twitch Snapper

```bash
sudo apt install python3.11-distutils
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

```bash
pipenv install
pipenv shell
python snapper/main.py
```

```bash
cd database
docker compose up -d
```

MariaDB is running on port 3306
phpMyAdmin is running on port 8080

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
