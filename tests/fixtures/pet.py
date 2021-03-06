import pytest


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
async def create_pet_uid(
    create_test_client, create_app_headers, create_store_uid
):
    # create app and store
    response = await create_test_client.post(
        "/pets/",
        json=pet_dict(store_uid=create_store_uid),
        headers=create_app_headers,
    )
    body = await response.json
    yield body["pet"]["uid"]
