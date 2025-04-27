import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings.settings import settings
from src.backend.auth.database.database import get_db, SessionLocal


@pytest.fixture(scope="session")
def test_db_engine():
    """Provide a database engine for the tests"""
    engine = create_engine(
        settings.POSTGRES_DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW
    )
    yield engine

@pytest.fixture(scope="function")
def test_session(test_db_engine):
    """Provide a database session for the tests"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def db_session(test_session):
    """Fixture for database session for testing.

    This fixture provides a database session for testing, and it ensures that
    any changes made to the database during a test are rolled back after the
    test is complete. This prevents tests from affecting each other.
    """
    connection = test_session.connection()
    transaction = connection.begin()
    
    # Replace the get_db generator with a function that uses the testing session.
    def override_get_db():
        yield test_session

    # Replace the original get_db dependency with our override function.
    from src.backend.auth.database.database import get_db as original_get_db
    from fastapi import Depends
    import inspect
    original_get_db.__globals__["Depends"] = lambda: Depends(override_get_db)

    # Run the test
    yield test_session

    # Rollback the changes made during the test
    transaction.rollback()
    connection.close()