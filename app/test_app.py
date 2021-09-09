import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from db import metadata
from app.models import app_table

# Create this tests' tables
@pytest.fixture
def create_app_tables(create_db):
    print("Creating Test Tables")
    engine = create_engine(create_db["DB_URI"])
    metadata.bind = engine
    metadata.create_all()


def app_dict():
    return dict(app_id="myapp", app_secret="test123")


@pytest.mark.asyncio
async def test_app_creation(create_test_client, create_app_tables):
    # basic create
    response = await create_test_client.post("/apps/", json=app_dict())
    body = await response.json
    assert response.status_code == 201
    assert body.get("result") == "ok"

    # app already exists
    response = await create_test_client.post("/apps/", json=app_dict())
    body = await response.json
    assert response.status_code == 400
    assert body.get("error_code") == "APP_ID_ALREADY_EXISTS"

    # missing secret
    app_dict_2 = dict(app_id="myapp2")
    response = await create_test_client.post("/apps/", json=app_dict_2)
    body = await response.json
    assert response.status_code == 400
    assert body.get("error_code") == "MALFORMED_DATA"
    assert (
        body.get("field_errors").get("app_secret")[0]
        == "Missing data for required field."
    )

    # malformed data
    app_dict_2 = dict(app_id="myapp2", app_secret="test 123")
    response = await create_test_client.post("/apps/", json=app_dict_2)
    body = await response.json
    assert response.status_code == 400
    assert body.get("error_code") == "MALFORMED_DATA"
    assert body.get("field_errors").get("app_secret")[0] == "No space allowed"
