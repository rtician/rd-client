from unittest.mock import patch

import pytest

from rd_client import MissingAuthorizationError


class MockedRequest:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def test_no_access_token(rd_client):
    assert rd_client.missing_token


def test_no_access_token_returns_false(rd_client):
    rd_client.access_token = '123123123'
    assert rd_client.missing_token == False


def test_no_access_token_raised(rd_client):
    with pytest.raises(MissingAuthorizationError) as exc_info:
        rd_client.no_access_token()

    message = 'No access token found. Visit the site'
    url = 'https://api.rd.services/auth/dialog?client_id=123&redirect_uri=https%3A//foo.bar'

    assert message in exc_info.value.args[0]
    assert url in exc_info.value.args[1]


@patch('rd_client.client.RDClient.no_access_token')
def test_authorize_with_no_token(no_access_token_mock, rd_client):
    rd_client.authorize()

    no_access_token_mock.assert_called_once_with()

@patch('rd_client.client.RDClient._generate_token')
def test_authorize_with_no_token(generate_token_mock, rd_client):
    rd_client.access_token = '123123'
    rd_client.authorize()

    generate_token_mock.assert_called_once_with()


@patch('rd_client.client.RDClient.post')
def test_generate_token_with_code(post_mock, rd_client):
    rd_client.code = 'code'
    post_mock.return_value = MockedRequest(
        {
            'access_token': 'access_token',
            'refresh_token': 'refresh_token'
        },
        200
    )

    rd_client._generate_token()

    post_mock.assert_called_once_with('/auth', data={
        'client_id': '123',
        'client_secret': '456',
        'code': 'code'
    })

    assert rd_client.access_token == 'access_token'
    assert rd_client.refresh_token == 'refresh_token'



@patch('rd_client.client.RDClient.post')
def test_generate_token_with_refresh_token(post_mock, rd_client):
    rd_client.access_token = 'access_token'
    rd_client.refresh_token = 'refresh_token'
    post_mock.return_value = MockedRequest(
        {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        },
        200
    )

    rd_client._generate_token()

    post_mock.assert_called_once_with('/auth', data={
        'client_id': '123',
        'client_secret': '456',
        'refresh_token': 'refresh_token'
    })

    assert rd_client.access_token == 'new_access_token'
    assert rd_client.refresh_token == 'new_refresh_token'


@patch('rd_client.client.RDClient.post')
def test_generate_token_with_error(post_mock, rd_client):
    post_mock.return_value = MockedRequest({}, 400)

    rd_client._generate_token()

    assert rd_client.access_token is None
    assert rd_client.refresh_token is None
