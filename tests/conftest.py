import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["PYTEST_USE_FAKE_REDIS"] = "1"

import pytest
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Ensure models are imported before create_all
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test_engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
