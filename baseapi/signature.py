import hmac
import hashlib


class BodyDigestSignature:
    def __init__(self, secret, header='sign'):
        self.secret = secret.encode()
        self.header = header

    def __call__(self, request):
        body = request.body
        try:
            body = body.encode()
        except Exception:
            pass
        signature = hmac.new(self.secret, body, digestmod=hashlib.sha512).hexdigest()
        request.headers[self.header] = signature
        return request
