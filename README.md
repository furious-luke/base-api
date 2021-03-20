# BaseAPI

Easily create maintainable API clients.

## Rationale

Building other Python based API clients I found that there was a
tendency to end up with a "mega-class", containing most of the
definitions of my API. BaseAPI tries to keep unrelated API concepts
separate, hopefully making for an easier maintenance experience.

## Installation

PyPi is the easiest way to install:

``` bash
pip install baseapi
```

## Usage

### Creating a client

Normally the `Client` class is inherited to create your own client
class:

``` python
from baseapi import Client


class MyClient(Client):
    DEFAULT_URL = 'https://my-api.com'
```

Here we've set our default API URL. This can also be set during the
creation of the client:

``` python
client = MyClient(url='https://localhost')
```

### Creating APIs

To populate your client with functions to access your API use
individual API classes. These reflect an isolated part of your overall
API.

As an example, you may have an authorization component to your API. To
add authorization to your client library, you may create a file called
`auth.py`:

``` python
from baseapi.apis import GraphqlApi


class AuthApi(GraphqlApi):
    def login(self, username, password):
        login_query = '...'
        data = {
            'username': username,
            'password': password
        }
        return self.perform_query(login_query, data)

    def logout(self):
        logout_query = '...'
        return self.perform_query(logout_query)
```

Once you have this slice of your API ready, you can add it to your
client by specifying it during the client class definition:

``` python
from baseapi import Client


class MyClient(Client):
    DEFAULT_URL = 'https://my-api.com'
    DEFAULT_APIS = (
        'auth',
    )
```

In this case, `auth.py` must be placed in your `PYTHONPATH`, most
likely alongside your client class file. Now, you may access the APIs
methods on your client as such:

```python
client = MyClient()
client.login('username', 'password')
```

There are currently two API types supported, GraphQL and Rest. The
same `auth` API as above, but using Rest instead:

``` python
from baseapi.apis import RestApi


class AuthApi(RestApi):
    def login(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        return self.post('/login', data)

    def logout(self):
        return self.post('/logout')
```

### Exposing methods to the client

The methods in an API that get exposed to a client are chosen based on
a leading underscore. Those without an underscore are automatically
added to the client class, while those with an underscore are treated
as private.

So, as an example, a local validation method could be added to an API
as such:

``` python
from baseapi.apis import RestApi


class MyApi(RestApi):
    def get_something(self, type):
        self._validate_type(type)
        return self.get('/api/something, data={'type': type})

    def _validate_type(self, type):
        # Do validation.
        pass
```
