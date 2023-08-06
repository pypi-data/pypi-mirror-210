import mercadopago

from ..MuviBase import MuviBase


class CardToken(MuviBase):
    def __init__(self, processor: str, sdk: mercadopago.SDK):
        super().__init__(processor)
        self.sdk = sdk

    def create(self, card: dict):
        if 'mercadopago_id' in card:
            card['id'] = card['mercadopago_id']

        data = {
            'card_id': card['id']
        }
        try:
            card_token_response = self.sdk.card_token().create(data)
        except:
            return self.error(
                message='error_cant_create_token',
                status=400
            )
        if card_token_response['status'] > 299:
            return self.error(response=card_token_response['response'], status=card_token_response['status'])

        # Para estandarizar la response con decidir
        if 'first_six_digits' in card:
            card_token_response['response']['bin'] = card['first_six_digits']
        elif 'bin' in card:
            card_token_response['response']['bin'] = card['bin']

        for f in ['last_four_digits', 'expiration_month', 'expiration_year', 'cardholder']:
            card_token_response['response'][f] = card[f] if f in card else None

        return self.ok(response=card_token_response['response'], status=card_token_response['status'])
