import pytest
from sqlalchemy import create_engine

from db import metadata

# Create this tests' tables
@pytest.fixture
def create_test_tables(create_db):
    print("Creating Test Tables")
    engine = create_engine(create_db["DB_URI"])
    metadata.bind = engine
    metadata.create_all()
