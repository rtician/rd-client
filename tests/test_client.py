from unittest.mock import patch

import pytest

from rd_client import MissingAuthorizationError


def test_no_access_token(rd_station):
    assert rd_station.missing_token


def test_no_access_token_returns_false(rd_station):
    rd_station.access_token = '123123123'
    assert rd_station.missing_token == False


def test_no_access_token_raised(rd_station):
    with pytest.raises(MissingAuthorizationError) as exc_info:
        rd_station.no_access_token()

    message = 'No access token found. Visit the site'
    url = 'https://api.rd.services/auth/dialog?client_id=123&redirect_uri=https%3A//foo.bar'

    assert message in exc_info.value.args[0]
    assert url in exc_info.value.args[1]


@patch('rd_client.client.RDStation.no_access_token')
def test_authorize_with_no_token(no_access_token_mock, rd_station):
    rd_station.authorize()

    no_access_token_mock.assert_called_once_with()

@patch('rd_client.client.RDStation._generate_token')
def test_authorize_with_no_token(generate_token_mock, rd_station):
    rd_station.access_token = '123123'
    rd_station.authorize()

    generate_token_mock.assert_called_once_with()
