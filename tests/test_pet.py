import pytest

from .fixtures.common import create_test_tables
from .fixtures.app import app_dict, create_app_headers
from .fixtures.store import store_dict, create_store_uid
from .fixtures.pet import pet_dict, create_pet_uid
from tests.utils import get_specific_dict_item


@pytest.mark.asyncio
async def test_pet_creation(
    create_test_client,
    create_test_tables,
    create_app_headers,
    create_store_uid,
):
    # create pet
    response = await create_test_client.post(
        "/pets/", json=pet_dict(create_store_uid), headers=create_app_headers
    )
    body = await response.json
    assert body["pet"]["name"] == pet_dict(create_store_uid)["name"]
    assert response.status_code == 201

    # missing required field
    pet_dict_2 = pet_dict(create_store_uid)
    del pet_dict_2["name"]
    response = await create_test_client.post(
        "/pets/", json=pet_dict_2, headers=create_app_headers
    )
    body = await response.json
    assert body["error_code"] == "MALFORMED_DATA"
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_pet_get(
    create_test_client,
    create_test_tables,
    create_app_headers,
    create_store_uid,
    create_pet_uid,
):
    # get the store
    response = await create_test_client.get(
        f"/pets/{create_pet_uid}",
        headers=create_app_headers,
    )
    body = await response.json
    assert response.status_code == 200
    assert body["pet"]["uid"] == create_pet_uid

    # not found pet
    response = await create_test_client.get(
        f"/pets/not-found",
        headers=create_app_headers,
    )
    assert response.status_code == 404

    # bad credentials
    headers = {
        "X-APP-ID": create_app_headers["X-APP-ID"],
        "X-APP-TOKEN": "wrong-token",
    }
    response = await create_test_client.get(
        f"/pets/{create_pet_uid}",
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_pets_get(
    create_test_client,
    create_test_tables,
    create_app_headers,
    create_store_uid,
    create_pet_uid,
):
    # check the store is returned in list
    response = await create_test_client.get(
        "/pets/", headers=create_app_headers
    )
    body = await response.json
    assert response.status_code == 200
    assert len(body.get("pets")) == 1
    assert body.get("pets")[0]["name"] == pet_dict(create_store_uid)["name"]

    # create 29 more pets
    for i in range(1, 29):
        await create_test_client.post(
            "/pets/",
            json=pet_dict(create_store_uid),
            headers=create_app_headers,
        )

    # check there's 10 stores and a first page
    response = await create_test_client.get(
        "/pets/", headers=create_app_headers
    )
    body = await response.json
    assert response.status_code == 200
    assert len(body.get("pets")) == 10

    # check there's a next page link
    next_page_item = get_specific_dict_item(body.get("links"), ("rel", "next"))
    assert next_page_item.get("href") == "/pets/?page=2"

    # create a second store
    second_store = store_dict()
    second_store["neighborhood"] = "Soho"
    response = await create_test_client.post(
        "/stores/", json=second_store, headers=create_app_headers
    )
    body = await response.json
    second_store_uid = body["store"]["uid"]

    # create 10 pets on second store
    for i in range(1, 29):
        await create_test_client.post(
            "/pets/",
            json=pet_dict(second_store_uid),
            headers=create_app_headers,
        )

    # check we get 10 pets on second store
    response = await create_test_client.get(
        f"/store/{second_store_uid}/pets/", headers=create_app_headers
    )
    body = await response.json
    # assert response.status_code == 200
    # assert len(body.get("pets")) == 10
