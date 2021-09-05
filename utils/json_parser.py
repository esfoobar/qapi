from typing import TYPE_CHECKING
from quart import abort
from marshmallow import ValidationError

from utils.api_responses import fail

if TYPE_CHECKING:
    from quart import Request
    from marshmallow.schema import Schema


async def get_json_payload(request: "Request", schema: "Schema") -> dict:
    try:
        json_payload = schema.load(await request.get_json())
        pass
    except ValidationError as err:
        fail(err.messages)

    return json_payload
