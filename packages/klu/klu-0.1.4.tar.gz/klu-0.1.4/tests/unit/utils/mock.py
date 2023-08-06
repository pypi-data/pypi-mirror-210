from typing import Any
from unittest.mock import MagicMock

from asyncmock import AsyncMock


class APIClientMock:
    def __init__(self, *_args: Any, **_kwargs: Any):
        self.session = MagicMock()

    async def get(self):
        return {}

    async def post(self, *_args: Any, **_kwargs: Any):
        return {"success": True}

    async def put(self, *_args: Any, **_kwargs: Any):
        return {"success": True}

    async def delete(self, *_args: Any, **_kwargs: Any):
        return {"success": True}


def get_api_client_mock():
    return APIClientMock


def client_get_function_mock(side_effect: Any):
    return AsyncMock(side_effect=side_effect)


def get_return_value_side_effect(return_value: Any):
    return lambda *args, **kwargs: return_value
