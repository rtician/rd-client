import pytest

from rd_client import RDClient


@pytest.fixture
def rd_client():
    return RDClient('123', '456', 'https://foo.bar')
