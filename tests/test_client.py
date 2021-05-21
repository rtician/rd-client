from unittest.mock import patch

import pytest

from rd_client import MissingAuthorizationError


class MockedRequest:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


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


@patch('rd_client.client.RDClient.post')
def test_generate_token_with_code(post_mock, rd_station):
    rd_station.code = 'code'
    post_mock.return_value = MockedRequest(
        {
            'access_token': 'access_token',
            'refresh_token': 'refresh_token'
        },
        200
    )

    rd_station._generate_token()

    post_mock.assert_called_once_with('/auth', data={
        'client_id': '123',
        'client_secret': '456',
        'code': 'code'
    })

    assert rd_station.access_token == 'access_token'
    assert rd_station.refresh_token == 'refresh_token'



@patch('rd_client.client.RDClient.post')
def test_generate_token_with_refresh_token(post_mock, rd_station):
    rd_station.access_token = 'access_token'
    rd_station.refresh_token = 'refresh_token'
    post_mock.return_value = MockedRequest(
        {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        },
        200
    )

    rd_station._generate_token()

    post_mock.assert_called_once_with('/auth', data={
        'client_id': '123',
        'client_secret': '456',
        'refresh_token': 'refresh_token'
    })

    assert rd_station.access_token == 'new_access_token'
    assert rd_station.refresh_token == 'new_refresh_token'


@patch('rd_client.client.RDClient.post')
def test_generate_token_with_error(post_mock, rd_station):
    post_mock.return_value = MockedRequest({}, 400)

    rd_station._generate_token()

    assert rd_station.access_token is None
    assert rd_station.refresh_token is None
