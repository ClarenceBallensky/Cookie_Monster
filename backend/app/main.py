# CURRENT TASK: Design Postgres schema (#17)
# - Finish remaining tables
# --------------------------------------------------------------------
# INSTRUCTIONS:
# Tables for policy claims, cookie/vendor lookups, and per-site comparison results.
# --------------------------------------------------------------------
import os
import psycopg2
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, text, Column, String, Integer, JSON, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://dev:dev@db:5432/privacy_inspector"
)
engine = create_engine(DATABASE_URL)

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
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

# --------------------------------------------------------------------
# SCHEMA CREATION

# Base acts as connection to db
Base = declarative_base()

# Each session is separated via SessionLocal (ensures user sessions are NOT combined globally)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# CONTRACT 2
class Cookie(Base):
    __tablename__ = "cookie"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String)
    domain = Column(String)

    # Column attributes below belong to the claims JSON variable
    category = Column(String)
    purpose = Column(String)
    does_or_does_not = Column(String)
    entity = Column(String)
    confidence = Column(Float)

# CONTRACT 3
class ObservedCookie(Base):
    __tablename__ = "observed cookie"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String)
    visited_at = Column(String)

    # Column attributes below belong to the cookie JSON variable 
    name = Column(String)
    known_vendor = Column(String)
    category = Column(String)

# CONTRACT 4
class ConclusionData(Base):
    __tablename__ = "conclusion data"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String)
    generated_at = Column(String)

    # Column attributes below belong to the quadrants dictionary Nvariable
    observed_disclosed = Column(String)
    observed_undisclosed = Column(String)
    not_observed_disclosed = Column(String)
    not_observed_not_disclosed = Column(String)
        
# Creates a connection to the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# pydantic model
class CookieBase(BaseModel):
    policy_id: str
    domain: str
    claim:  list[dict[str, str]]

class ObservedCookieBase(BaseModel):
    policy_id: str
    domain: str
    claim:  list[dict[str, str]]

class ConclusionDataBase(BaseModel):
    policy_id: str
    domain: str
    claim:  list[dict[str, str]]
db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/cookies")
def add_cookies(cookie: CookieBase, db: db_dependency):
    db_cookie = Cookie(policy_id=cookie.policy_id, domain=cookie.domain, claim=cookie.claim)
    db.add(db_cookie)
    db.commit()
    db.refresh(db_cookie)

    


# TODO Backend: real endpoints go here, e.g.
# GET /comparison/{domain} -> four-quadrant result (see docs/DATA_CONTRACTS.md, Contract 4)