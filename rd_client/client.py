import json
from urllib import parse

import requests

from rd_client.errors import MissingAuthorizationError


class API:
    base_url = 'https://api.rd.services'
    access_token = None

    @property
    def headers(self):
        d = {'Content-Type': 'application/json'}
        if self.access_token is not None:
            d['Authorization'] = 'Bearer {token}'.format(token=self.access_token)
        return d

    @staticmethod
    def supports_body(method):
        return method.lower() in ('delete', 'patch', 'post', 'put')

    def build_url(self, uri):
        return '{base_url}{uri}'.format(base_url=self.base_url, uri=uri)

    def request(self, method, uri, params, data, headers):
        request_method = getattr(requests, method.lower())

        updated_headers = self.headers
        if headers is not None:
            updated_headers.update(headers)

        url = self.build_url(uri)
        if self.supports_body(method):
            response = request_method(
                url,
                data=json.dumps(data) if data else None,
                headers=updated_headers
            )
        else:
            response = request_method(url, params=params, headers=updated_headers)

        return response

    def get(self, uri, params=None, data=None, headers=None):
        return self.request('get', uri, params, data, headers)

    def delete(self, uri, params=None, data=None, headers=None):
        return self.request('delete', uri, params, data, headers)

    def post(self, uri, params=None, data=None, headers=None):
        return self.request('post', uri, params, data, headers)

    def patch(self, uri, params=None, data=None, headers=None):
        return self.request('patch', uri, params, data, headers)

    def put(self, uri, params=None, data=None, headers=None):
        return self.request('put', uri, params, data, headers)


class RDClient(API):
    def __init__(self, client_id, client_secret, redirect_uri, access_token=None, code=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.code = code
        self.refresh_token = None

    @property
    def missing_token(self):
        return self.access_token is None

    def authorize(self):
        if self.missing_token and self.code is None:
            self.no_access_token()
        else:
            self._generate_token()

    def no_access_token(self):
        url = '{base_url}/auth/dialog?client_id={client_id}&redirect_uri={redirect_uri}'.format(
            base_url=self.base_url,
            client_id=self.client_id,
            redirect_uri=parse.quote(self.redirect_uri)
        )
        message = 'No access token found. Visit the site "{}" to start the authorization process'

        raise MissingAuthorizationError(message.format(url), url)

    def _generate_token(self):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        if self.refresh_token is not None:
            data['refresh_token'] = self.refresh_token
        else:
            data['code'] = self.code

        response = self.post('/auth', data=data)

        if response.status_code == 200:
            response_json = response.json()
            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']
