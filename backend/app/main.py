import os

from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI(title="Privacy Inspector API")

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://dev:dev@db:5432/privacy_inspector"
)


@app.get("/")
def root():
    return {"service": "privacy-inspector-api", "status": "running"}


@app.get("/health")
def health():
    """Confirms the API process itself is up."""
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    """Confirms the API can actually reach Postgres."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}


# TODO Backend: real endpoints go here, e.g.
# GET /comparison/{domain} -> four-quadrant result (see docs/DATA_CONTRACTS.md, Contract 4)