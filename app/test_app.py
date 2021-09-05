import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from db import metadata
from app.models import app_table

# Create this tests' tables
@pytest.fixture
def create_app_tables(create_db):
    print("Creating Counter Tables")
    engine = create_engine(create_db["DB_URI"])
    metadata.bind = engine
    metadata.create_all()


def app_dict():
    return dict(name="myapp", secret="test123")


@pytest.mark.asyncio
async def test_app_creation(create_test_client, create_app_tables):
    response = await create_test_client.post("/apps/", json=app_dict())
    body = await response.json
    assert response.status_code == 201
    assert body.get("result") == "ok"
