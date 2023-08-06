from klu.model.models import Model
from tests.integration import client
from tests.integration.utils.common import string_uuid


def get_unique_test_model_llm() -> str:
    return f"test-model-llm-{string_uuid()}"


async def create_model(**kwargs) -> Model:
    return await client.models.create(
        llm=kwargs.get("llm", "gpt-4"),
        # TODO When endpoints for ws_model_provider are added, replace 0 with an actual id of provider,
        #  retrieved from a listing endpoint (or creation endpoint if that one is provided)
        workspace_model_provider_id=kwargs.get("workspace_model_provider_id", 1),
    )


class ModelSingleton:
    model = None

    async def get_default_model(self, **kwargs) -> Model:
        if not self.model:
            self.model = await create_model(**kwargs)

        return self.model
