from typing import Optional
import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from fixtures.common import create_test_tables
from fixtures.app import app_dict, _create_app_headers
from fixtures.store import store_dict, _create_store_uid
from fixtures.pet import pet_dict, _create_pet_uid


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


@pytest.mark.asyncio
async def test_pet_get(
    create_test_client,
    create_test_tables,
    _create_app_headers,
    _create_store_uid,
    _create_pet_uid,
):
    # get the store
    response = await create_test_client.get(
        f"/pets/{_create_pet_uid}",
        headers=_create_app_headers,
    )
    body = await response.json
    assert response.status_code == 200
    assert body["pet"]["uid"] == _create_pet_uid

    # not found pet
    response = await create_test_client.get(
        f"/pets/not-found",
        headers=_create_app_headers,
    )
    assert response.status_code == 404

    # bad credentials
    headers = {
        "X-APP-ID": _create_app_headers["X-APP-ID"],
        "X-APP-TOKEN": "wrong-token",
    }
    response = await create_test_client.get(
        f"/pets/{_create_pet_uid}",
        headers=headers,
    )
    assert response.status_code == 403
