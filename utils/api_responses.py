from typing import Optional


def success(data: dict) -> dict:
    data["result"] = "ok"
    return data


def fail(data: dict) -> dict:
    data["result"] = "error"
    return data
