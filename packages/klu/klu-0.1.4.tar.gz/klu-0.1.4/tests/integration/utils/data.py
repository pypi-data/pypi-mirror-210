from klu.data.models import Data

from tests.integration import client
from tests.integration.utils.common import string_uuid
from tests.integration.utils.actions import create_action
from tests.integration.utils.sessions import create_session


def get_unique_test_data_input() -> str:
    return f"test-data-input-{string_uuid()}"


async def create_data(**kwargs) -> Data:
    action_guid = kwargs.get("action_guid")
    if not action_guid:
        action = await create_action()
        action_guid = action.guid

    session_guid = kwargs.get("session_guid")
    if not session_guid:
        session_guid = await create_session(action_guid=action_guid)
        session_guid = session_guid.guid

    return await client.data.create(
        action_guid=action_guid,
        session_guid=session_guid,
        rating=kwargs.get("rating", 0),
        meta_data=kwargs.get("meta_data", None),
        issue=kwargs.get("issue", "test-data-issue"),
        input=kwargs.get("input", "test-data-input"),
        output=kwargs.get("output", "test-data-output"),
        action=kwargs.get("action", "test-data-action"),
        correction=kwargs.get("correction", "test-data-correction"),
    )


class DataSingleton:
    data = None

    async def get_default_data(self, **kwargs) -> Data:
        if not self.data:
            action = await create_action()
            session = await create_session(action_guid=action.guid)

            self.data = await create_data(action_guid=action.guid, session_guid=session.guid, **kwargs)

        return self.data
