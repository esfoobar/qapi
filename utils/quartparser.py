from typing import TYPE_CHECKING

from quart import abort
from marshmallow import ValidationError

if TYPE_CHECKING:
    from quart import Request
    from marshmallow.schema import Schema


async def get_params(request: "Request", schema: "Schema") -> dict:
    try:
        params = schema.load(await request.get_json())
        pass
    except ValidationError as err:
        abort(
            response=err.messages,
            status=400,
        )

    return params
