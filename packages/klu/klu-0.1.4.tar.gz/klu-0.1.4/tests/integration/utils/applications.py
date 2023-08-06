from klu.application.models import Application

from tests.integration import client
from tests.integration.utils.common import string_uuid


def get_unique_test_app_name() -> str:
    return f"test-app-name-{string_uuid()}"


async def create_application(**kwargs) -> Application:
    return await client.applications.create(
        name=kwargs.get("name", "test-app-name"),
        app_type=kwargs.get("app_type", "test-app-type"),
        description=kwargs.get("description", "test-app-description"),
    )


class AppSingleton:
    application = None

    async def get_default_app(self, **kwargs) -> Application:
        if not self.application:
            self.application = await create_application(**kwargs)

        return self.application
