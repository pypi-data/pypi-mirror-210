import pytest

from klu.client.klu import KluClient

from tests.integration.constants import API_KEY
from tests.integration.utils.models import create_model

client = KluClient(API_KEY)


@pytest.mark.asyncio
async def test_crud_model():
    test_model_llm = "gpt-3.5-turbo"
    create_response = await create_model(llm=test_model_llm)
    created_instance_guid = create_response.guid

    assert create_response.llm == test_model_llm
    assert created_instance_guid is not None

    get_response = await client.models.get(created_instance_guid)
    assert get_response is not None
    assert get_response.guid == created_instance_guid

    new_model_llm = "gpt-4"
    update_response = await client.models.update(
        created_instance_guid,
        llm=new_model_llm,
    )
    assert update_response.llm == new_model_llm

    delete_response = await client.models.delete(created_instance_guid)
    assert delete_response.guid == created_instance_guid
