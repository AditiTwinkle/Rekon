"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from rekon.db.schemas.base import Base


@pytest.fixture(scope="function")
def test_db_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Create test database session."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db_session(test_db_session):
    """Alias for test_db_session."""
    return test_db_session
