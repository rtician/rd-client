import json
from urllib import parse

import requests

from rd_client.errors import MissingAuthorizationError


class RDClient:
    base_url = 'https://api.rd.services'
    client_id = None
    client_secret = None
    access_token = None
    supports_body = {'post', 'patch'}

    @property
    def headers(self):
        d = {'Content-Type': 'application/json'}
        if self.access_token is not None:
            d['Authorization'] = 'Bearer {token}'.format(token=access_token)
        return d

    def build_url(self, uri):
        return '{base_url}{uri}'.format(base_url=self.base_url, uri=uri)

    def request(self, method, uri, params, data, headers):
        request_method = getattr(requests, method.lower())

        updated_headers = self.headers
        if headers is not None:
            updated_headers.update(headers)

        url = self.build_url(uri)
        if method.lower() in self.supports_body:
            response = request_method(url, data=json.dumps(data), headers=updated_headers)
        else:
            response = request_method(url, params=self.params, headers=updated_headers)

        return response

    def get(self, uri, params=None, data=None, headers=None):
        return self.request('get', uri, params, data, headers)

    def post(self, uri, params=None, data=None, headers=None):
        return self.request('post', uri, params, data, headers)

    def patch(self, uri, params=None, data=None, headers=None):
        return self.request('patch', uri, params, data, headers)


class RDStation(RDClient):
    def __init__(self, client_id, client_secret, redirect_uri, access_token=None, code=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.code = code
        self.refresh_token = None

    @property
    def missing_token(self):
        return self.access_token is None

    def authorize(self):
        if self.missing_token:
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

        if response.status == 200:
            response_json = response.json()
            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']
