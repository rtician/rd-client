import pytest

from rd_client import RDStation


@pytest.fixture
def rd_station():
    return RDStation('123', '456', 'https://foo.bar')
