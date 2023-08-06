from klu.action.models import Action

from tests.integration import client
from tests.integration.utils.common import string_uuid
from tests.integration.utils.models import create_model
from tests.integration.utils.applications import create_application


def get_unique_test_action_name() -> str:
    return f"test-action-name-{string_uuid()}"


async def create_action(**kwargs) -> Action:
    app_guid = kwargs.get("app_guid")
    if not app_guid:
        app = await create_application()
        app_guid = app.guid

    model_guid = kwargs.get("model_guid")
    if not model_guid:
        model = await create_model()
        model_guid = model.guid

    return await client.actions.create(
        app_guid=app_guid,
        model_guid=model_guid,
        name=kwargs.get("name", "test-action-name"),
        model_config=kwargs.get("model_config", None),
        action_type=kwargs.get("action_type", "simple"),
        prompt=kwargs.get("prompt", "Tell me about it"),
        description=kwargs.get("description", "test-action-description"),
    )


class ActionSingleton:
    _action = None

    async def get_default_action(self, **kwargs) -> Action:
        if not self._action:
            model = await create_model()
            app = await create_application()

            self._action = await create_action(
                app_guid=app.guid, model_guid=model.guid, **kwargs
            )

        return self._action
