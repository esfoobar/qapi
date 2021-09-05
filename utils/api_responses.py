from typing import Optional


def success(data: dict) -> dict:
    data["result"] = "ok"
    return data


def fail(error_code: str) -> dict:
    data = {}
    data["result"] = "error"
    data["error_code"] = error_code
    return data
