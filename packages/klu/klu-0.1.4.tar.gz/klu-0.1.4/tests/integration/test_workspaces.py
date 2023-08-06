import pytest

from klu.client.klu import KluClient

from tests.integration.constants import API_KEY
from tests.integration.utils.applications import create_application
from tests.integration.utils.workspace import create_workspace, get_unique_test_ws_name, WorkspaceSingleton

client = KluClient(API_KEY)
workspace_singleton = WorkspaceSingleton()


# TODO requires creation of an api_key for new workspace because app workspace is retrieved based on the api_key provided
# @pytest.mark.asyncio
# async def test_get_workspace_apps():
#     workspace = await workspace_singleton.get_default_workspace()
#     await create_application()
#
#     response = await client.workspace.get_workspace_apps(workspace.project_guid)
#     assert len(response) == 1


# TODO requires creation of an api_key for new workspace
# @pytest.mark.asyncio
# async def test_get_workspace_models():
#     workspace = await workspace_singleton.get_default_workspace()
#     await create_model()
#
#     response = await client.workspace.get_workspace_models(workspace.project_guid)
#     assert len(response) > 0


# TODO requires creation of an api_key for new workspace
@pytest.mark.asyncio
# async def test_get_workspace_indices():
#     workspace = await workspace_singleton.get_default_workspace()
#
#     response = await client.workspace.get_workspace_indices(workspace.project_guid)
#     assert len(response) > 0


@pytest.mark.asyncio
async def test_list_workspaces():
    response = await client.workspace.list()
    assert len(response) > 0


@pytest.mark.asyncio
async def test_crud_workspaces():
    unique_ws_name = get_unique_test_ws_name()
    create_response = await create_workspace(name=unique_ws_name)
    workspace_guid = create_response.project_guid

    assert create_response.name == unique_ws_name
    assert create_response.created_by_id is not None

    get_response = await client.workspace.get(workspace_guid)
    assert get_response.name == unique_ws_name

    new_ws_name = get_unique_test_ws_name()
    update_response = await client.workspace.update(workspace_guid, new_ws_name)
    assert update_response.name == new_ws_name

    delete_response = await client.workspace.delete(workspace_guid)
    assert delete_response.project_guid == workspace_guid
