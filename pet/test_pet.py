from typing import Optional
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


def pet_dict(store_uid: str):
    return dict(
        name="Mac",
        species="Dog",
        breed="Shitzu",
        age=11,
        store_uid=store_uid,
        price="766.65",
        received_date="2016-11-11T12:12:01Z",
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
@pytest.fixture
async def _create_store_uid(create_test_client, _create_app_headers):
    # create app and store
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )
    body = await response.json
    yield body["store"]["uid"]


@pytest.mark.asyncio
async def test_pet_creation(
    create_test_client,
    create_test_tables,
    _create_app_headers,
    _create_store_uid,
):
    # create pet
    response = await create_test_client.post(
        "/pets/", json=pet_dict(_create_store_uid), headers=_create_app_headers
    )
    body = await response.json
    assert body["pet"]["name"] == pet_dict(_create_store_uid)["name"]
    assert response.status_code == 201

    # missing required field
    pet_dict_2 = pet_dict(_create_store_uid)
    del pet_dict_2["name"]
    response = await create_test_client.post(
        "/pets/", json=pet_dict_2, headers=_create_app_headers
    )
    body = await response.json
    assert body["error_code"] == "MALFORMED_DATA"
    assert response.status_code == 400
