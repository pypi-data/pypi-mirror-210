import uuid

import pytest

from klu.client.klu import KluClient

from tests.integration.constants import API_KEY
from tests.integration.utils.applications import AppSingleton
from tests.integration.utils.data import create_data

client = KluClient(API_KEY)
app_singleton = AppSingleton()


@pytest.mark.asyncio
async def test_crud_data():
    test_data_output = f"test-data-output-{str(uuid.uuid4())}"
    create_response = await create_data(output=test_data_output)
    created_instance_guid = create_response.guid

    assert create_response.output == test_data_output
    assert created_instance_guid is not None

    get_response = await client.data.get(created_instance_guid)
    assert get_response is not None
    assert get_response.guid == created_instance_guid

    new_test_data_output = f"new-test-data-output-{str(uuid.uuid4())}"
    update_response = await client.data.update(
        get_response.guid,
        output=new_test_data_output,
    )
    assert update_response.output == new_test_data_output

    delete_response = await client.data.delete(created_instance_guid)
    assert delete_response.guid == created_instance_guid
