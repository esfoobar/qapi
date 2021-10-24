import pytest
from quart import current_app
from sqlalchemy import select
from datetime import datetime, timedelta

from db import metadata
from app.models import app_table, app_access_table
from .fixtures.common import create_test_tables
from .fixtures.app import app_dict


@pytest.mark.asyncio
async def test_app_creation(create_test_client, create_test_tables):
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


@pytest.mark.asyncio
async def test_app_token_generation(
    create_test_app, create_test_client, create_test_tables
):
    # create app
    response = await create_test_client.post("/apps/", json=app_dict())
    body = await response.json
    assert response.status_code == 201
    assert body.get("result") == "ok"

    # generate access token
    response = await create_test_client.post(
        "/apps/access_token/",
        json=app_dict(),
    )
    body = await response.json
    token = body.get("token")
    assert token is not None

    # define token query for reuse
    # remember to use sqlalchemy.select instead of app_table.select when doing joins
    app_access_query = select([app_access_table.c.id, app_table.c.id]).where(
        (app_access_table.c.app_id == app_table.c.id)
        & (app_table.c.name == app_dict()["app_id"])
    )

    # check that only one token is in database
    async with create_test_app.app_context():
        conn = current_app.dbc
        app_access_tokens = await conn.fetch_all(query=app_access_query)
        assert len(app_access_tokens) == 1

    # gen another token
    response = await create_test_client.post(
        "/apps/access_token/",
        json=app_dict(),
    )
    body = await response.json
    token = body.get("token")
    assert token is not None

    # check that still only one token is in database
    async with create_test_app.app_context():
        conn = current_app.dbc
        app_access_tokens = await conn.fetch_all(query=app_access_query)
        assert len(app_access_tokens) == 1

    # bad credentials
    app_dict_2 = dict(app_id="myapp2", app_secret="test123")
    response = await create_test_client.post(
        "/apps/access_token/",
        json=app_dict_2,
    )
    body = await response.json
    assert response.status_code == 403
    assert body.get("error_code") == "INCORRECT_CREDENTIALS"

    # test expired token
    # IMPORTANT: Only do after implenting GET stores endpoint
    now = datetime.utcnow().replace(second=0, microsecond=0)
    expires = now + timedelta(days=-31)

    async with create_test_app.app_context():
        conn = current_app.dbc
        app_access_expire_query = app_access_table.update(
            app_access_table.c.id == app_access_tokens[0]["id"]
        ).values({"expires": expires})
        await conn.execute(app_access_expire_query)

    response = await create_test_client.get(
        "/stores/",
        headers={"X-APP-ID": app_dict()["app_id"], "X-APP-TOKEN": token},
    )
    body = await response.json
    assert response.status_code == 403
    assert body.get("error") == "TOKEN_EXPIRED"
