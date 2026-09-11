# Backend

## Running database migrations

After changing a SQLAlchemy model, generate a migration:

    docker compose exec api alembic revision --autogenerate -m "describe your change"

Then apply it:

    docker compose exec api alembic upgrade head

Alembic reads DATABASE_URL from .env automatically (see alembic/env.py) —
no need to edit alembic.ini.