import mercadopago

from ..MuviBase import MuviBase


def _format(response):
    return {
        'id': response['id'],
        'card_type': response['payment_method']['payment_type_id'],
        'card_brand': response["payment_method"]["name"],
        'last_four_digits': response['last_four_digits'],
        'issuer': {
            'name': response['issuer']['name']
        },
        'cardholder': {
            'name': response['cardholder']['name']
        },
        'expiration_month': response['expiration_month'],
        'expiration_year': response['expiration_year'],
    }


class Card(MuviBase):
    def __init__(self, processor: str, sdk: mercadopago.SDK):
        super().__init__(processor)
        self.sdk = sdk

    def create(self, customer_id: str, card_token: str):
        card_data = {'token': card_token}
        mp_response = self.sdk.card().create(customer_id, card_data)

        if mp_response['status'] < 400:
            return self.ok(response=_format(mp_response['response']), status=mp_response['status'])
        return self.error(message=mp_response['response']['error'], status=mp_response['status'])

    def get(self, customer_id: str, card_id: str) -> dict:
        mp_response = self.sdk.card().get(customer_id, card_id)
        if mp_response['status'] < 400:
            card = mp_response['response']
            return self.ok(response=_format(card), status=mp_response['status'])
        return self.error(message=mp_response['response']['message'], status=mp_response['status'])

    def list_all(self, customer_id: str):
        mp_response = self.sdk.card().list_all(customer_id)
        if mp_response['status'] > 299:
            return self.error(message='Customer not found', status=mp_response['status'])
        cards = mp_response['response']
        return self.ok(response={'results': [_format(card) for card in cards]}, status=mp_response['status'])
