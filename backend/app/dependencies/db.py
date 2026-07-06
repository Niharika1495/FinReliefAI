from typing import Generator
from sqlalchemy.orm import Session
from app.database.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency provider that yields a transaction-safe SQLAlchemy database session
    for route handlers, and guarantees connection release and cleanup upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
