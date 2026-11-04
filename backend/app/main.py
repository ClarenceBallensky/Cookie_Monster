import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text, Column, String, Integer, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Annotated
from typing_extensions import TypedDict
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

    # Column attributes below belong to the quadrants dictionary
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

# pydantic MODELS to verify VALID data types

class claimDict(TypedDict):
    category: str 
    purpose: str | None
    does_or_does_not: str
    entity: str | None
    confidence: float

class CookieBase(BaseModel):
    policy_id: str
    domain: str
    # claims attribute validates data inside the dictionary via the claimDict template class.
    claims : list[claimDict] = Field(min_length=1, max_length=1)
# ------------------------------------------------------------------
class cookieDict(TypedDict):
    name: str
    known_vendor: str | None
    category: str | None

class ObservedCookieBase(BaseModel):
    domain: str
    visited_at: str
    # cookies attribute validates data inside the dictionary via the cookieDict template class.
    cookies : list[cookieDict] = Field(min_length=1, max_length=1)
# ------------------------------------------------------------------
class ConclusionDataBase(BaseModel):
    domain: str
    generated_at : str
    quadrants : dict[str, Annotated[list[str], Field(min_length=1, max_length=1)]] = Field(min_length=4, max_length=4)
# ------------------------------------------------------------------

db_dependency = Annotated[Session, Depends(get_db)]

# POST routes to add data to tables listed above
@app.post("/cookies")
def add_cookies(cookie: CookieBase, db: db_dependency):
    db_cookie = Cookie(
        policy_id=cookie.policy_id, 
        domain=cookie.domain,

        # Prevents python returning a keyerror if a certain attribute key is NOT found. 
        category = cookie.claims[0].get('category'),
        purpose = cookie.claims[0].get('purpose'),
        does_or_does_not = cookie.claims[0].get('does_or_does_not'),
        entity = cookie.claims[0].get('entity'),
        confidence = cookie.claims[0].get('confidence'))
    db.add(db_cookie)
    db.commit()
    db.refresh(db_cookie)

@app.post("/observedCookies")
def add_observed_cookies(observedCookie: ObservedCookieBase, db: db_dependency):
    db_observed_cookie = ObservedCookie( 
        domain=observedCookie.domain, 
        visited_at=observedCookie.visited_at,
        name = observedCookie.cookies[0].get('name'),
        known_vendor = observedCookie.cookies[0].get('known_vendor'),
        category = observedCookie.cookies[0].get('category'))
    db.add(db_observed_cookie)
    db.commit()
    db.refresh(db_observed_cookie)

@app.post("/conclusionData")
def add_conclusion_data(conclusionData: ConclusionDataBase, db: db_dependency):
    db_conclusion_data = ConclusionData( 
        domain=conclusionData.domain, 
        generated_at=conclusionData.generated_at,
        # Column attributes below belong to the dictionary quadrants
        observed_disclosed = conclusionData.quadrants.get('observed_disclosed')[0],
        observed_undisclosed = conclusionData.quadrants.get('observed_undisclosed')[0],
        not_observed_disclosed = conclusionData.quadrants.get('not_observed_disclosed')[0],
        not_observed_not_disclosed = conclusionData.quadrants.get('not_observed_not_disclosed')[0])
    db.add(db_conclusion_data)
    db.commit()
    db.refresh(db_conclusion_data)

# TODO Backend: real endpoints go here, e.g.
# GET /comparison/{domain} -> four-quadrant result (see docs/DATA_CONTRACTS.md, Contract 4)