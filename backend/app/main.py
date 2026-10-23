# CURRENT TASK: Design Postgres schema (#17)
# --------------------------------------------------------------------

# INSTRUCTIONS:
# Tables for policy claims, cookie/vendor lookups, and per-site comparison results.
# --------------------------------------------------------------------
import os
import psycopg2
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, text, Column, String, Integer, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://dev:dev@db:5432/privacy_inspector"
)


# --------------------------------------------------------------------
# Health check API endpoints

app = FastAPI(title="Privacy Inspector API")
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

# --------------------------------------------------------------------
# SCHEMA CREATION

# THREE basic parts of FASTapi
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initializes the database in postgres
Base.metadata.create_all(bind=engine)


class Cookie(Base):
    __tablename__ = "cookie"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String)
    domain = Column(String)
    # Claim will store an array of dictionaries, breaking down a claim into its important parts.
    claim = Column(JSON)

    def __init__ (self, policy_id : String, domain : String, claim : JSON):
        self.policy_id = policy_id
        self.domain = domain
        self.claim = claim

        
# Creates a connection to the database
def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()

# pydantic model
class CookieBase(BaseModel):
    policy_id: str
    domain: str
    claim:  list[dict[str, str]]

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/cookies")
async def add_cookies(cookie: CookieBase, db: db_dependency):
    db_cookie = Cookie(policy_id=cookie.policy_id, domain=cookie.domain, claim=cookie.claim)
    db.add(db_cookie)
    db.commit()
    db.refresh()
    


# TODO Backend: real endpoints go here, e.g.
# GET /comparison/{domain} -> four-quadrant result (see docs/DATA_CONTRACTS.md, Contract 4)