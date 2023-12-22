#/bin/bash

docker compose -f docker-compose.dev.yaml up -d && sleep 5
pipenv install
pipenv run alembic upgrade head
export PYTHONPATH=$(pwd) && pipenv run python alembic/seed_dev.py
