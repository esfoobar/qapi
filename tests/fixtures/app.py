import pytest


def app_dict():
    return dict(app_id="myapp", app_secret="test123")


@pytest.mark.asyncio
@pytest.fixture
async def create_app_headers(create_test_client):
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
