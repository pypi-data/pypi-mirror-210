import math
from uuid import uuid4

import pytest

from klu.client.klu import KluClient

from tests.integration.constants import API_KEY
from tests.integration.utils.applications import (
    create_application,
    get_unique_test_app_name,
)
from tests.integration.utils.data import create_data
from tests.integration.utils.actions import create_action
from tests.integration.utils.models import ModelSingleton

client = KluClient(API_KEY)

model_singleton = ModelSingleton()


@pytest.mark.asyncio
async def test_list_app_data():
    default_model = await model_singleton.get_default_model()

    app = await create_application()
    action = await create_action(app_guid=app.guid, model_guid=default_model.guid)

    await create_data(action_guid=action.guid)
    await create_data(action_guid=action.guid)

    data = await client.applications.get_app_data(app.guid)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_app_actions():
    default_model = await model_singleton.get_default_model()

    app = await create_application()
    await create_action(app_guid=app.guid, model_guid=default_model.guid)
    await create_action(app_guid=app.guid, model_guid=default_model.guid)

    actions = await client.applications.get_app_actions(app.guid)
    assert len(actions) == 2


@pytest.mark.asyncio
async def test_list_all_apps():
    await create_application()
    await create_application()

    apps = await client.applications.list()
    assert len(apps) >= 2


@pytest.mark.asyncio
async def test_get_app_page():
    await create_application()
    await create_application()
    await create_application()
    await create_application()

    apps_page_1 = await client.applications.fetch_single_page(1, limit=2)
    apps_page_2 = await client.applications.fetch_single_page(2, limit=2)

    assert len(apps_page_1) == 2
    assert len(apps_page_2) == 2

    for index, page_2_app in enumerate(apps_page_2):
        page_1_app = apps_page_1[index]
        assert page_2_app.created_at > page_1_app.created_at


@pytest.mark.asyncio
async def test_apps_fetch_next_page_odd_total():
    all_apps = await client.applications.list()

    per_page = 2
    initial_len = len(all_apps)

    is_odd_total = initial_len % per_page != 0
    if not is_odd_total:
        await create_application()

        is_odd_total = True
        initial_len += 1

    total_pages = math.ceil(initial_len / per_page)

    all_pages = []
    for page in range(1, total_pages + 1):
        is_last_page = page == total_pages
        apps_page = await client.applications.fetch_next_page(limit=2)
        all_pages.extend(apps_page)

        expected_page_len = 1 if is_last_page and is_odd_total else 2
        assert len(apps_page) == expected_page_len

    assert len(all_pages) == initial_len


@pytest.mark.asyncio
async def test_crud_applications():
    test_app_name = get_unique_test_app_name()

    create_response = await create_application(
        name=test_app_name,
        app_type="test-app-type",
        description="test-app-description",
    )

    assert create_response.name == test_app_name
    assert create_response.guid is not None
    assert create_response.created_by_id is not None

    created_instance_guid = create_response.guid
    get_response = await client.applications.get(created_instance_guid)
    assert get_response.guid == created_instance_guid

    new_app_name = f"new-test-app-name-{str(uuid4())}"
    update_response = await client.applications.update(
        created_instance_guid,
        name=new_app_name,
    )
    assert update_response.name == new_app_name

    delete_response = await client.applications.delete(created_instance_guid)
    assert delete_response.guid == created_instance_guid
