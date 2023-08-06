import math
import pytest

# import asyncio

from tests.integration import client
from tests.integration.utils.data import create_data
from tests.integration.utils.models import ModelSingleton
from tests.integration.utils.applications import AppSingleton
from tests.integration.utils.actions import create_action, ActionSingleton

app_singleton = AppSingleton()
model_singleton = ModelSingleton()
action_singleton = ActionSingleton()


# @pytest.mark.asyncio
# async def test_run_action_prompt_returns_streaming_url():
#     action = await action_singleton.get_default_action()
#     action_prompt_result = await client.actions.run_action_prompt(
#         action.guid,
#         "What are the risks of Artificial general intelligence?",
#         streaming=True,
#     )
#     action_streaming_url = action_prompt_result.streaming_url
#     assert action_streaming_url is not None
#
#     await asyncio.sleep(5)
#     data = None
#     async for data in client.actions.get_action_streaming_data(action_streaming_url):
#         assert data is not None
#
#     assert data == "No messages to stream"


@pytest.mark.asyncio
async def test_run_action_prompt():
    action = await action_singleton.get_default_action()
    action_prompt_result = await client.actions.run_action_prompt(
        action.guid, "test", "test", False
    )

    assert action_prompt_result.msg
    assert action_prompt_result.streaming_url is None


@pytest.mark.asyncio
async def test_run_playground_prompt():
    playground_prompt_result = await client.actions.run_playground_prompt("test", 1)
    assert playground_prompt_result.msg is not None


@pytest.mark.asyncio
async def test_get_action_data():
    action = await action_singleton.get_default_action()
    await create_data(action_guid=action.guid)

    action_data = await client.actions.get_action_data(action.guid)
    assert len(action_data) > 0


@pytest.mark.asyncio
async def test_list_all_actions():
    default_app = await app_singleton.get_default_app()
    default_model = await model_singleton.get_default_model()
    await create_action(app_guid=default_app.guid, model_guid=default_model.guid)
    await create_action(app_guid=default_app.guid, model_guid=default_model.guid)

    actions = await client.actions.list()
    assert len(actions) >= 2


@pytest.mark.asyncio
async def test_get_action_page():
    default_app = await app_singleton.get_default_app()
    default_model = await model_singleton.get_default_model()
    await create_action(app_guid=default_app.guid, model_guid=default_model.guid)
    await create_action(app_guid=default_app.guid, model_guid=default_model.guid)
    await create_action(app_guid=default_app.guid, model_guid=default_model.guid)
    await create_action(app_guid=default_app.guid, model_guid=default_model.guid)

    actions_page_1 = await client.actions.fetch_single_page(1, limit=2)
    actions_page_2 = await client.actions.fetch_single_page(2, limit=2)

    assert len(actions_page_1) == 2
    assert len(actions_page_2) == 2

    for index, page_2_action in enumerate(actions_page_2):
        page_1_action = actions_page_1[index]
        assert page_2_action.created_at > page_1_action.created_at


@pytest.mark.asyncio
async def test_actions_fetch_next_page_odd_total():
    all_actions = await client.actions.list()

    per_page = 2
    initial_len = len(all_actions)

    is_odd_total = initial_len % per_page != 0
    if not is_odd_total:
        await create_action()

        is_odd_total = True
        initial_len += 1

    total_pages = math.ceil(initial_len / per_page)

    all_pages = []
    for page in range(1, total_pages + 1):
        is_last_page = page == total_pages
        actions_page = await client.actions.fetch_next_page(limit=2)
        all_pages.extend(actions_page)

        expected_page_len = 1 if is_last_page and is_odd_total else 2
        assert len(actions_page) == expected_page_len

    assert len(all_pages) == initial_len


@pytest.mark.asyncio
async def test_crud_actions():
    default_app = await app_singleton.get_default_app()
    default_model = await model_singleton.get_default_model()

    create_response = await create_action(
        app_guid=default_app.guid,
        model_guid=default_model.guid,
    )
    action_guid = create_response.guid

    assert create_response.app_id == default_app.id
    assert create_response.model_id == default_model.id

    get_response = await client.actions.get(action_guid)
    assert get_response.guid == action_guid

    new_app_name = "new-test-app-name"
    update_response = await client.actions.update(action_guid, name=new_app_name)
    assert update_response.name == new_app_name
    delete_response = await client.actions.delete(action_guid)
    assert delete_response.guid == action_guid
