import uuid

import pytest

from klu.client.klu import KluClient
from klu.data_index.models import FileData, DataIndexStatusEnum

from tests.integration.constants import API_KEY, TEST_FILE_PATH
from tests.integration.utils.common import string_uuid

client = KluClient(API_KEY)


@pytest.mark.asyncio
async def test_get_pre_signed_url():
    response = await client.data_index.get_index_upload_pre_signed_url(
        f"{uuid.uuid4()}.pdf"
    )
    assert response.url is not None
    assert response.fields is not None
    assert response.object_url is not None


@pytest.mark.asyncio
async def test_upload_file():
    response = await client.data_index.upload_index_file(
        FileData(
            file_path=TEST_FILE_PATH,
            file_name=f"test-file-{uuid.uuid4()}.pdf",
        )
    )
    assert response is not None


@pytest.mark.asyncio
async def test_create_data_index_with_file():
    response = await client.data_index.create(
        splitter="some-splitter",
        description="test data index",
        name=f"test-data-index-{uuid.uuid4()}",
        file_data=FileData(
            file_path=TEST_FILE_PATH,
            file_name=f"test-file-{uuid.uuid4()}.pdf",
        ),
    )
    assert response.file_url is not None


@pytest.mark.asyncio
async def test_check_data_index_status():
    file_name = f"test-file-{uuid.uuid4()}.pdf"
    new_data_index = await client.data_index.create(
        splitter="some-splitter",
        description="test data index",
        name=f"test-data-index-{uuid.uuid4()}",
        file_data=FileData(
            file_name=file_name,
            file_path=TEST_FILE_PATH,
        ),
    )
    await client.data_index.process_data_index(new_data_index.guid, file_name)
    response = await client.data_index.get_status(new_data_index.guid)

    assert response == DataIndexStatusEnum.PENDING


@pytest.mark.asyncio
async def test_crud_data_index():
    test_data_index_name = f"test-data-index-name-{str(uuid.uuid4())}"
    create_response = await client.data_index.create(
        splitter="some-splitter",
        name=test_data_index_name,
        description="test data index",
    )
    created_instance_guid = create_response.guid

    assert create_response.name == test_data_index_name
    assert create_response.guid is not None
    assert create_response.created_by_id is not None

    get_response = await client.data_index.get(created_instance_guid)
    assert get_response.guid == created_instance_guid

    new_data_index_name = f"new-test-data-index-name-{string_uuid()}"
    update_response = await client.data_index.update(
        created_instance_guid,
        name=new_data_index_name,
    )
    assert update_response.name == new_data_index_name

    delete_response = await client.data_index.delete(created_instance_guid)
    assert delete_response.guid == created_instance_guid
