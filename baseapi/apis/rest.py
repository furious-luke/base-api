import json
import requests
from urllib.parse import urlencode

from ..exceptions import QueryException
from ..utils import remove_trailing_slash, merge_headers

from .api import Api


class RestApi(Api):
    IGNORED_ATTRIBUTES = Api.IGNORED_ATTRIBUTES | set([
        'get',
        'post',
        'put',
        'patch',
        'delete',
        'options',
        'perform_request',
    ])

    def get(self, path, data=None, headers=None):
        return self.perform_request('get', path, data=data, headers=headers)

    def post(self, path, data=None, headers=None):
        return self.perform_request('post', path, data=data, headers=headers)

    def put(self, path, data=None, headers=None):
        return self.perform_request('put', path, data=data, headers=headers)

    def patch(self, path, data=None, headers=None):
        return self.perform_request('patch', path, data=data, headers=headers)

    def delete(self, path, data=None, headers=None):
        return self.perform_request('delete', path, data=data, headers=headers)

    def options(self, path, data=None, headers=None):
        return self.perform_request('options', path, data=data, headers=headers)

    def perform_request(self, method, path, data=None, headers=None):
        url = remove_trailing_slash(self.client.url)
        url = f'{url}{path}'
        auth_headers = {}
        if self.client.jwt:
            auth_headers['Authorization'] = f'Bearer {self.client.jwt}'
        headers = {
            **auth_headers,
            **merge_headers(self.client.headers, headers),
        }
        if self.client.debug:
            print(f'Request: {url} ({method})')
            print('  Headers:')
            print(f'    {json.dumps(headers, indent=6)}')
            print('  Data:')
            print(f'    {json.dumps(data, indent=6)}')
        if method == 'get':
            url = f'{url}?{urlencode(data)}'
            data = None
        response = getattr(requests, method)(
            url,
            json=data,
            headers=headers,
        )
        if response.status_code not in self.SUCCESS_RESPONSE_CODES:
            msg = response.content
            raise QueryException(
                f'API error: {msg}',
                status_code=response.status_code,
                body=response.content,
                headers=response.headers,
            )
        response_data = response.json()
        return response_data
