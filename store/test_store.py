import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from db import metadata


# Create this tests' tables
@pytest.fixture
def create_test_tables(create_db):
    print("Creating Test Tables")
    engine = create_engine(create_db["DB_URI"])
    metadata.bind = engine
    metadata.create_all()


def app_dict():
    return dict(app_id="myapp", app_secret="test123")


def store_dict():
    return dict(
        neighborhood="Chelsea",
        street_address="123 Main Street",
        city="New York",
        state="NY",
        zip_code="10001",
        phone="212-555-1234",
        live=True,
    )


@pytest.mark.asyncio
@pytest.fixture
async def _create_app_headers(create_test_client):
    # app create
    response = await create_test_client.post("/apps/", json=app_dict())

    # get token
    response = await create_test_client.post(
        "/apps/access_token/",
        json=app_dict(),
    )
    body = await response.json
    token = body.get("token")
    yield {"X-APP-ID": app_dict()["app_id"], "X-APP-TOKEN": token}


@pytest.mark.asyncio
async def test_store_creation(
    create_test_client, create_test_tables, _create_app_headers
):
    # create store
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )
    body = await response.json
    assert response.status_code == 201
    assert body["store"]["zip_code"] == store_dict()["zip_code"]
