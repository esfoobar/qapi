from typing import TYPE_CHECKING
from marshmallow import ValidationError
from quart import abort, make_response, jsonify

from utils.api_responses import fail

if TYPE_CHECKING:
    from quart import Request
    from marshmallow.schema import Schema


async def get_json_payload(request: "Request", schema: "Schema") -> dict:
    try:
        json_payload = schema.load(await request.get_json())
        pass
    except ValidationError as err:
        response = await make_response(
            jsonify(
                fail(error_code="MALFORMED_DATA", field_errors=err.messages)
            ),
            400,
        )
        abort(response)

    return json_payload
