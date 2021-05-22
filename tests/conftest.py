import pytest

from rd_client import RDClient
from rd_client.client import API


@pytest.fixture
def rd_client():
    return RDClient('123', '456', 'https://foo.bar')


@pytest.fixture
def base_api():
    return API()
