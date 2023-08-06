from klu.workspace.models import Workspace

from tests.integration import client
from tests.integration.utils.common import string_uuid


def get_unique_test_ws_name() -> str:
    return f"test-ws-name-{string_uuid()}"


async def create_workspace(**kwargs) -> Workspace:
    return await client.workspace.create(
        name=kwargs.get("name", "test-ws-name"),
        slug=kwargs.get("slug", "test-ws-slug"),
    )


class WorkspaceSingleton:
    workspace = None

    async def get_default_workspace(self, **kwargs) -> Workspace:
        if not self.workspace:
            self.workspace = await create_workspace(**kwargs)

        return self.workspace
