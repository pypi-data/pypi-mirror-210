from klu.session.models import Session

from tests.integration import client
from tests.integration.utils.common import string_uuid
from tests.integration.utils.actions import create_action


def get_unique_test_data_input() -> str:
    return f"test-data-input-{string_uuid()}"


async def create_session(**kwargs) -> Session:
    action_guid = kwargs.get("action_guid")
    if not action_guid:
        action = await create_action()
        action_guid = action.guid

    return await client.sessions.create(
        action_guid=action_guid,
    )


class SessionSingleton:
    session = None

    async def get_default_session(self, **kwargs) -> Session:
        if not self.session:
            action = await create_action()
            self.session = await create_session(action_guid=action.guid, **kwargs)

        return self.session
