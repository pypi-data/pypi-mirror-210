from klu.data_index.models import DataIndex

from tests.integration import client
from tests.integration.utils.common import string_uuid


def get_unique_test_data_index_name() -> str:
    return f"test-data-index-name-{string_uuid()}"


async def create_data_index(**kwargs) -> DataIndex:
    return await client.data_index.create(
        splitter=kwargs.get("splitter", None),
        file_data=kwargs.get("file_data", None),
        name=kwargs.get("name", "test-data-index-name"),
        description=kwargs.get("description", "test-data-index-description"),
    )


class DataIndexSingleton:
    data_index = None

    async def get_default_data_index(self, **kwargs) -> DataIndex:
        if not self.data_index:
            self.data_index = await create_data_index(**kwargs)

        return self.data_index
