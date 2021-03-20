import inspect
from importlib import import_module

from .apis import Api
from .exceptions import ClientException


class Client:
    DEFAULT_URL = None
    DEFAULT_APIS = ()

    def __init__(self, url=None, jwt=None, session=None, debug=False):
        self.url = url or self.DEFAULT_URL
        self.debug = debug
        self.jwt = jwt
        self.apis = []
        self.headers = {}
        self.session = session
        self.load_apis()
        if self.session:
            self.session.load(self)

    def load_apis(self):
        for api_name in self.DEFAULT_APIS:
            module = import_module(api_name)
            for cls in module.__dict__.values():
                if self.is_valid_api(cls):
                    self.add_api(cls(self))

    def is_valid_api(self, cls):
        try:
            return issubclass(cls, Api) and cls != Api
        except TypeError:
            return False

    def add_api(self, api):
        self.apis.append(api)
        any_exposed = self._are_any_exposed(api)
        for attr_name in dir(api):
            attr = getattr(api, attr_name)
            if any_exposed:
                if getattr(attr, 'expose', False):
                    self._expose_api_method(attr_name, attr)
            else:
                if self._should_expose(attr_name, attr, api):
                    self._expose_api_method(attr_name, attr)

    def set_jwt(self, jwt):
        self.jwt = jwt
        if self.session:
            self.session.save(self)

    def is_authenticated(self):
        return bool(self.jwt)

    def _are_any_exposed(self, api):
        for attr_name in dir(api):
            attr = getattr(api, attr_name)
            if getattr(attr, 'expose', False):
                return True
        return False

    def _should_expose(self, attr_name, attr, api):
        return (
            attr_name[0] != '_'
            and inspect.ismethod(attr)
            and attr_name not in api.IGNORED_ATTRIBUTES
        )

    def _expose_api_method(self, name, method):
        if getattr(self, name, None) is not None:
            raise ClientException(f'Name already exists on client: {name}')
        setattr(self, name, method)
