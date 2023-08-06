#!/usr/bin/env python
"""Tests for `action` module functions"""
import pytest

from aiohttp import web
from unittest.mock import patch

from klu.client.klu import KluClient
from tests.unit.action.utils import get_action_data
from klu.application.errors import ApplicationNotFoundError
from tests.unit.utils.mock import (
    get_api_client_mock,
    client_get_function_mock,
    get_return_value_side_effect,
)


@pytest.mark.asyncio
async def test_get_app_actions_converts_response_to_dataclass_provided_valid_response_dicts(
    klu_client: KluClient,
):
    with patch(
        "klu.common.client.APIClient", new_callable=get_api_client_mock
    ) as client_mock:
        action_1_guid = "test_action_1"
        action_2_guid = "test_action_2"

        test_action_1 = get_action_data(guid=action_1_guid)
        test_action_2 = get_action_data(guid=action_2_guid)

        client_mock.get = client_get_function_mock(
            get_return_value_side_effect([test_action_1, test_action_2])
        )
        result = await klu_client.applications.get_app_actions("test")

        assert len(result) == 2
        assert result[0].guid == action_1_guid
        assert result[1].guid == action_2_guid


@pytest.mark.asyncio
async def test_get_app_actions_raises_klu_error_provided_404_response_from_api(
    klu_client: KluClient,
):
    with patch(
        "klu.common.client.APIClient", new_callable=get_api_client_mock
    ) as client_mock:
        client_mock.get = client_get_function_mock(web.HTTPNotFound())
        with pytest.raises(Exception) as exc_info:
            await klu_client.applications.get_app_actions("test")

        assert exc_info.type is ApplicationNotFoundError
