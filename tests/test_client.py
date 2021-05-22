import json
from unittest.mock import patch

import pytest

from rd_client import MissingAuthorizationError


class MockedRequest:
    def __init__(self, json_data=None, status_code=None):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class TestAPI:
    def setup_method(self):
        self.url = 'https://api.rd.services'
        self.base_headers = {'Content-Type': 'application/json'}

    def test_headers(self, base_api):
        headers = base_api.headers
        assert headers == {'Content-Type': 'application/json'}

    def test_headers_with_access_token(self, base_api):
        base_api.access_token = '123'
        headers = base_api.headers
        assert headers == {'Content-Type': 'application/json', 'Authorization': 'Bearer 123'}

    def test_supports_body(self, base_api):
        for method in ('delete', 'patch', 'post', 'put'):
            assert base_api.supports_body(method)

        assert base_api.supports_body('get') == False

    def test_build_url(self, base_api):
        url = base_api.build_url('/something')

        assert url == '{}/something'.format(self.url)

    @patch('rd_client.client.requests')
    def test_get(self, requests_mock, base_api):
        requests_mock.get.return_value = {}
        base_api.get('/uri')

        requests_mock.get.assert_called_once_with(
            '{}/uri'.format(self.url),
            params=None,
            headers=self.base_headers
        )

    @patch('rd_client.client.requests')
    def test_delete(self, requests_mock, base_api):
        requests_mock.delete.return_value = {}
        base_api.delete('/uri')

        requests_mock.delete.assert_called_once_with(
            '{}/uri'.format(self.url),
            data=None,
            headers=self.base_headers
        )

    @patch('rd_client.client.requests')
    def test_patch(self, requests_mock, base_api):
        requests_mock.patch.return_value = {}
        base_api.patch('/uri')

        requests_mock.patch.assert_called_once_with(
            '{}/uri'.format(self.url),
            data=None,
            headers=self.base_headers
        )

    @patch('rd_client.client.requests')
    def test_post(self, requests_mock, base_api):
        requests_mock.post.return_value = {}
        base_api.post('/uri')

        requests_mock.post.assert_called_once_with(
            '{}/uri'.format(self.url),
            data=None,
            headers=self.base_headers
        )

    @patch('rd_client.client.requests')
    def test_put(self, requests_mock, base_api):
        requests_mock.put.return_value = {}
        base_api.put('/uri')

        requests_mock.put.assert_called_once_with(
            '{}/uri'.format(self.url),
            data=None,
            headers=self.base_headers
        )

    @patch('rd_client.client.requests')
    def test_requests(self, requests_mock, base_api):
        requests_mock.patch.return_value = MockedRequest()
        response = base_api.request('patch', '/uri', None, None, None)

        requests_mock.patch.assert_called_once_with(
            '{}/uri'.format(self.url),
            data=None,
            headers=self.base_headers
        )
        assert isinstance(response, MockedRequest)

    @patch('rd_client.client.requests')
    def test_requests_with_data(self, requests_mock, base_api):
        requests_mock.patch.return_value = MockedRequest()

        response = base_api.request('patch', '/uri', None, {'key': 'value'}, None)
        requests_mock.patch.assert_called_once_with(
            '{}/uri'.format(self.url),
            data=json.dumps({'key': 'value'}),
            headers=self.base_headers
        )
        assert isinstance(response, MockedRequest)

        # Params cannot be passed for methods that supports body
        response = base_api.request('patch', '/uri', 'key=value', None, None)
        requests_mock.patch.assert_called_with(
            '{}/uri'.format(self.url),
            data=None,
            headers=self.base_headers
        )
        assert isinstance(response, MockedRequest)

    @patch('rd_client.client.requests')
    def test_requests_with_params(self, requests_mock, base_api):
        requests_mock.get.return_value = MockedRequest()

        response = base_api.request('get', '/uri', 'key=value', {'key': 'value'}, None)
        requests_mock.get.assert_called_once_with(
            '{}/uri'.format(self.url),
            params='key=value',
            headers=self.base_headers
        )
        assert isinstance(response, MockedRequest)

    @patch('rd_client.client.requests')
    def test_requests_with_headers(self, requests_mock, base_api):
        requests_mock.get.return_value = MockedRequest()

        response = base_api.request('get', '/uri', 'key=value', {'key': 'value'}, {'auth': '1'})
        requests_mock.get.assert_called_once_with(
            '{}/uri'.format(self.url),
            params='key=value',
            headers={'Content-Type': 'application/json', 'auth': '1'}
        )
        assert isinstance(response, MockedRequest)



class TestRDClient:
    def test_no_access_token(self, rd_client):
        assert rd_client.missing_token

    def test_no_access_token_returns_false(self, rd_client):
        rd_client.access_token = '123123123'
        assert rd_client.missing_token == False

    def test_no_access_token_raised(self, rd_client):
        with pytest.raises(MissingAuthorizationError) as exc_info:
            rd_client.no_access_token()

        message = 'No access token found. Visit the site'
        url = 'https://api.rd.services/auth/dialog?client_id=123&redirect_uri=https%3A//foo.bar'

        assert message in exc_info.value.args[0]
        assert url in exc_info.value.args[1]

    @patch('rd_client.client.RDClient.no_access_token')
    def test_authorize_with_no_token(self, no_access_token_mock, rd_client):
        rd_client.access_token = None
        rd_client.authorize()

        no_access_token_mock.assert_called_once_with()

    @patch('rd_client.client.RDClient._generate_token')
    def test_authorize_with_token(self, generate_token_mock, rd_client):
        rd_client.access_token = '123123'
        rd_client.authorize()

        generate_token_mock.assert_called_once_with()

    @patch('rd_client.client.RDClient.post')
    def test_generate_token_with_code(self, post_mock, rd_client):
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
    def test_generate_token_with_refresh_token(self, post_mock, rd_client):
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
    def test_generate_token_with_error(self, post_mock, rd_client):
        post_mock.return_value = MockedRequest({}, 400)

        rd_client._generate_token()

        assert rd_client.access_token is None
        assert rd_client.refresh_token is None
