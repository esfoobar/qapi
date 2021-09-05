from typing import Dict, Optional, Union, Any


def success(data: dict) -> dict:
    data["result"] = "ok"
    return data


def fail(
    error_code: Optional[str] = None,
    field_errors: Optional[Dict[Any, Any]] = None,
) -> dict:
    data: Dict[str, Union[str, dict]] = {}
    data["result"] = "error"
    if error_code:
        data["error_code"] = error_code
    if field_errors:
        data["field_errors"] = field_errors
    return data
