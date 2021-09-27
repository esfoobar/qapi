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
    # IMPORTANT: note that the _create_app_headers fixture is executed
    #            after its called the firss time and any subsequent calls
    #            to it just return the dict
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )
    body = await response.json
    assert response.status_code == 201
    assert body["store"]["zip_code"] == store_dict()["zip_code"]

    # create store without tokens
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers={}
    )
    body = await response.json
    assert response.status_code == 403

    # create store with wrong tokens
    headers = {
        "X-APP-ID": _create_app_headers["X-APP-ID"],
        "X-APP-TOKEN": "wrong-token",
    }
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=headers
    )
    body = await response.json
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_store_get(
    create_test_client, create_test_tables, _create_app_headers
):
    # create store
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )
    body = await response.json
    store = body["store"]

    # get the store
    response = await create_test_client.get(
        f"/stores/{store['uid']}",
        json=store_dict(),
        headers=_create_app_headers,
    )
    body = await response.json
    assert response.status_code == 200
    assert body["store"]["uid"] == store["uid"]

    # not found store
    response = await create_test_client.get(
        f"/stores/not-found",
        json=store_dict(),
        headers=_create_app_headers,
    )
    assert response.status_code == 404

    # bad credentials
    headers = {
        "X-APP-ID": _create_app_headers["X-APP-ID"],
        "X-APP-TOKEN": "wrong-token",
    }
    response = await create_test_client.get(
        f"/stores/{store['uid']}",
        json=store_dict(),
        headers=headers,
    )
    assert response.status_code == 403


def _get_specific_dict_item(dict_list: list, k_v_pair: tuple) -> Optional[dict]:
    k, v = k_v_pair
    return next((item for item in dict_list if item[k] == v), None)


@pytest.mark.asyncio
async def test_stores_get(
    create_test_client, create_test_tables, _create_app_headers
):
    # create one store
    await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )

    # check the store is returned in list
    response = await create_test_client.get(
        "/stores/", headers=_create_app_headers
    )
    body = await response.json
    assert response.status_code == 200
    assert len(body.get("stores")) == 1
    assert body.get("stores")[0]["city"] == store_dict()["city"]

    # create 29 more stores
    for i in range(1, 29):
        await create_test_client.post(
            "/stores/", json=store_dict(), headers=_create_app_headers
        )

    # check there's 10 stores and a first page
    response = await create_test_client.get(
        "/stores/", headers=_create_app_headers
    )
    body = await response.json
    assert response.status_code == 200
    assert len(body.get("stores")) == 10

    # check there's a next page link
    next_page_item = _get_specific_dict_item(body.get("links"), ("rel", "next"))
    assert next_page_item.get("href") == "/stores/?page=2"

    # grab the second page and check there's previous and next
    response = await create_test_client.get(
        next_page_item.get("href"), headers=_create_app_headers
    )
    body = await response.json

    # previus page
    next_page_item = _get_specific_dict_item(
        body.get("links"), ("rel", "previous")
    )
    assert next_page_item.get("href") == "/stores/?page=1"

    # next page
    next_page_item = _get_specific_dict_item(body.get("links"), ("rel", "next"))
    assert next_page_item.get("href") == "/stores/?page=3"

    # grab the third page and check there's previous and no next
    response = await create_test_client.get(
        next_page_item.get("href"), headers=_create_app_headers
    )
    body = await response.json

    # previus page
    next_page_item = _get_specific_dict_item(
        body.get("links"), ("rel", "previous")
    )
    assert next_page_item.get("href") == "/stores/?page=2"

    # next page
    next_page_item = _get_specific_dict_item(body.get("links"), ("rel", "next"))
    assert next_page_item == None


@pytest.mark.asyncio
async def test_stores_put(
    create_test_client, create_test_tables, _create_app_headers
):
    # create one store
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )
    body = await response.json
    original_store = body["store"]

    # modify store's neighborhood
    modified_store = store_dict()
    modified_store["neighborhood"] = "Upper West Side"

    response = await create_test_client.put(
        f"/stores/{original_store['uid']}",
        json=modified_store,
        headers=_create_app_headers,
    )
    body = await response.json
    assert response.status_code == 200
    assert body["store"]["neighborhood"] == modified_store["neighborhood"]

    # get an error on bad data
    modified_store = store_dict()
    modified_store["zip_code"] = "123"

    response = await create_test_client.put(
        f"/stores/{original_store['uid']}",
        json=modified_store,
        headers=_create_app_headers,
    )
    body = await response.json
    assert response.status_code == 400
    assert body["error_code"] == "MALFORMED_DATA"

    # check there's only one store in list (idempotency)
    response = await create_test_client.get(
        "/stores/", headers=_create_app_headers
    )
    body = await response.json
    assert len(body.get("stores")) == 1


@pytest.mark.asyncio
async def test_stores_delete(
    create_test_client, create_test_tables, _create_app_headers
):
    # create one store
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=_create_app_headers
    )
    body = await response.json
    original_store = body["store"]

    # delete store and check result 200
    response = await create_test_client.delete(
        f"/stores/{original_store['uid']}",
        headers=_create_app_headers,
    )
    body = await response.json
    assert response.status_code == 200

    # try to fetch same store get 404
    response = await create_test_client.get(
        f"/stores/{original_store['uid']}",
        headers=_create_app_headers,
    )
    body = await response.json
    assert response.status_code == 404

    # get stores list and it should be empty
    response = await create_test_client.get(
        "/stores/", headers=_create_app_headers
    )
    body = await response.json
    assert len(body.get("stores")) == 0
