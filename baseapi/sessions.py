from pathlib import Path
import json


class FileSession:
    """Cache credentials to the filesystem.

    This is intended for use during development when we don't want to
    have to keep fetching credentials before every test call.
    """
    def __init__(self, filename):
        self.filename = Path(filename)

    def save(self, client):
        if client.jwt:
            self._save_jwt(client)
        else:
            self._delete_jwt()
        if client.auth:
            self._save_auth(client)
        else:
            self._delete_auth()

    def load(self, client):
        try:
            with open(self.filename) as f:
                data = json.loads(f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return
        client.jwt = data.get('jwt')
        client.auth = data.get('auth')

    def _save_jwt(self, client):
        with open(self.filename, 'w') as f:
            f.write(json.dumps({'jwt': client.jwt}))

    def _save_auth(self, client):
        with open(self.filename, 'w') as f:
            f.write(json.dumps({'auth': client.auth}))

    def _delete_jwt(self):
        self.filename.unlink(missing_ok=True)

    def _delete_auth(self):
        self.filename.unlink(missing_ok=True)
