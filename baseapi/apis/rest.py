import os
import json
import requests
from functools import partial
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests_toolbelt.utils import dump
from urllib.parse import urlencode

from ..exceptions import QueryException
from ..utils import remove_trailing_slash, merge_headers

from .api import Api

DEFAULT_TIMEOUT = 5
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
)


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def assert_status_hook(response, *args, **kwargs):
    """Raise an error for any requests that have failed."""
    if not response.ok:
        raise QueryException(
            f'API error: {response.content}',
            status_code=response.status_code,
            body=response.content,
            headers=response.headers,
        )


def logging_hook(response, *args, **kwargs):
    """Log the request if logging is enabled."""
    if kwargs["debug"]:
        data = dump.dump_all(response)
        print(data.decode('utf-8'))


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
    api_timeout = DEFAULT_TIMEOUT

    def __init__(self, *args, **kwargs):
        """
        Create a requests session to send HTTP requests with.

        Add timeout and retry logic to the session, log full requests if
        debugging, and catch and re-raise any request errors.

        See also: https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
        """
        super().__init__(*args, **kwargs)
        self.timeout_adapter = TimeoutHTTPAdapter(
            max_retries=retries,
            timeout=self.api_timeout,
        )
        self.session = requests.Session()
        self.session.hooks["response"] = [partial(logging_hook, debug=self.client.debug), assert_status_hook]
        self.session.mount("http://", self.timeout_adapter)
        self.session.mount("https://", self.timeout_adapter)

    def get(self, path, data=None, headers=None, timeout=None):
        return self.perform_request('get', path, data=data, headers=headers, timeout=timeout)

    def post(self, path, data=None, headers=None, timeout=None):
        return self.perform_request('post', path, data=data, headers=headers, timeout=timeout)

    def put(self, path, data=None, headers=None, timeout=None):
        return self.perform_request('put', path, data=data, headers=headers, timeout=timeout)

    def patch(self, path, data=None, headers=None, timeout=None):
        return self.perform_request('patch', path, data=data, headers=headers, timeout=timeout)

    def delete(self, path, data=None, headers=None, timeout=None):
        return self.perform_request('delete', path, data=data, headers=headers, timeout=timeout)

    def options(self, path, data=None, headers=None, timeout=None):
        return self.perform_request('options', path, data=data, headers=headers, timeout=timeout)

    def perform_request(self, method, path, data=None, headers=None, timeout=None):
        url = remove_trailing_slash(self.client.url)
        url = f'{url}{path}'
        auth_headers = {}
        if self.client.jwt:
            auth_headers['Authorization'] = f'Bearer {self.client.jwt}'
        headers = {
            **auth_headers,
            **merge_headers(self.client.headers, headers),
        }

        if method == 'get' and data is not None:
            url = f'{url}?{urlencode(data)}'
            data = None

        return getattr(self.session, method)(
            url,
            json=data,
            headers=headers,
            timeout=timeout,
        ).json()
