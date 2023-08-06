import pytest

from klu.client.klu import KluClient


@pytest.fixture(scope="function")
def klu_client() -> KluClient:
    return KluClient("test_api_key")
