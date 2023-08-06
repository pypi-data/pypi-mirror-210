import json

import requests

from ..MuviBase import MuviBase


def _format(response):
    return {
        'email': response['email'],
        'first_name': response['nombre'],
        'last_name': response['apellido'],
    }


def _check(client: dict) -> dict:
    lista = {
        'nombre': None,
        'apellido': None,
        'celular': None,
        'email': None
    }
    for k in lista.keys():
        if k not in client:
            client[k] = lista[k]
    if 'domicilio' not in client:
        client['domicilio'] = {
            'altura': '1',
            'calle': '-'
        }
    else:
        if 'calle' not in client['domicilio']:
            client['domicilio']['calle'] = '-'
        if 'altura' not in client['domicilio']:
            client['domicilio']['altura'] = '1'

    return client


class Customer(MuviBase):
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

    def create(self, client: dict) -> dict:
        client = client.copy()
        client = _check(client)
        formatted_client = _format(client)
        customer = {
            'customer': {
                'name': '{} {}'.format(client['nombre'], client['apellido']),
                'identification': {
                    'type': 'dni',
                    'number': client['documento']
                }
            }
        }
        self.headers['apikey'] = self.public_key
        r = requests.post(self.url + '/tokens', headers=self.headers, data=json.dumps(customer))
        self.headers['apikey'] = self.private_key
        if r.status_code > 400:
            return self.error(response=r.json(), status=r.status_code)
        else:
            formatted_client['id'] = r.json()['id']
        return self.ok(response=formatted_client, status=r.status_code)

    def get(self, customer_id: str) -> dict:
        # No existen los datos del customer almacenados en decidir
        return self.error(message='Customer not found', status=404)

    def search(self, filters: dict):
        return self.error(message='Customer not found', status=404)
