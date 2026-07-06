from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.settings import settings

# SQLite compatibility arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread=False for multiple threads to access the connection
    connect_args = {"check_same_thread": False}

# Configure SQLAlchemy connection engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False  # Set to True in development if SQL log outputs are needed
)

# Register event listener to enforce foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Ensures that every SQLite connection executes the foreign keys PRAGMA,
    enabling cascade delete and constraint enforcement at the database level.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create SessionLocal class for instantiating individual database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base class for mapper mapping (SQLAlchemy models)
Base = declarative_base()
