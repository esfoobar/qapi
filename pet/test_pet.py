from typing import Optional
import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from fixtures.common import create_test_tables
from fixtures.app import app_dict, _create_app_headers
from fixtures.store import store_dict, _create_store_uid


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
