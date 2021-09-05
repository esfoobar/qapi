from typing import Optional
from quart import Response
from typing import Optional


def success(data: dict, status: Optional[int] = 200) -> "Response":
    data["result"] = "ok"
    return Response(data, status=status)


def fail(data: dict, status: Optional[int] = 400) -> "Response":
    data["result"] = "error"
    return Response(data, status=status)
