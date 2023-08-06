import requests
import json

from ..MuviBase import MuviBase


class CardToken(MuviBase):
    def __init__(self, processor: str, url: str, private_key: str, public_key: str):
        super().__init__(processor)
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, card: dict):
        if 'decidir_id' in card:
            card['id'] = card['decidir_id']

        body = {
            'token': card['id'],
            'security_code': '000' if 'security_code' not in card else card['security_code'],
        }
        self.headers['apikey'] = self.public_key
        r = requests.post(self.url + '/tokens', headers=self.headers, data=json.dumps(body))
        self.headers['apikey'] = self.private_key
        response = r.json()
        if r.status_code > 299:
            return self.error(response=response, message=response['error_type'], status=r.status_code)
        return self.ok(response=response, status=r.status_code)
