import pytest


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
async def create_store_uid(create_test_client, create_app_headers):
    # create app and store
    response = await create_test_client.post(
        "/stores/", json=store_dict(), headers=create_app_headers
    )
    body = await response.json
    yield body["store"]["uid"]
