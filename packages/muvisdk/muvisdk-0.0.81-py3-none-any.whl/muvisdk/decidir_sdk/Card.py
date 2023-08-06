import requests

from ..MuviBase import MuviBase

card_brand = {
    1: 'Visa',
    8: 'Diners',
    23: 'Tarjeta Shopping',
    24: 'Tarjeta Naranja',
    25: 'Pago Fácil',
    26: 'Rapipago',
    29: 'Italcred',
    30: 'Argencard',
    34: 'CoopePlus',
    37: 'Nexo',
    38: 'Credimás',
    39: 'Tarjeta Nevada',
    42: 'Nativa',
    43: 'Tarjeta Cencosud',
    44: 'Tarjeta Carrefour / Cetelem',
    45: 'Tarjeta PymeNacion',
    48: 'Caja de Pagos',
    50: 'BBPS',
    51: 'Cobro Express',
    52: 'Qida',
    54: 'Grupar',
    55: 'Patagonia 365',
    56: 'Tarjeta Club Día',
    59: 'Tuya',
    60: 'Distribution',
    61: 'Tarjeta La Anónima',
    62: 'CrediGuia',
    63: 'Cabal',
    64: 'Tarjeta SOL',
    65: 'American Express',
    103: 'Favacard',
    104: 'Mastercard',
    109: 'Nativa Prisma',
    111: 'American Express Prisma',
    
    # Debito
    31: 'Visa Débito',
    105: 'Mastercard Débito',
    106: 'Maestro',
    108: 'Cabal Débito'
}


def _card_type(payment_method_id):
    if payment_method_id in [31, 105, 106, 108]:
        return 'debit_card'
    return 'credit_card'


def _format(response, customer_id):
    return {
        'id': response['token'],
        'card_type': _card_type(response['payment_method_id']),
        'card_brand': card_brand[response['payment_method_id']],
        'last_four_digits': response['last_four_digits'],
        'issuer': {
            'name': card_brand[response['payment_method_id']]
        },
        'cardholder': {
            'name': response['card_holder']['name']
        },
        'expiration_month': int(response['expiration_month']),
        'expiration_year': int('20' + response['expiration_year']),
    }


class Card(MuviBase):
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

    def create(self, customer_id: str, card_token: str):
        """ Tokenizar la tarjeta

        :param customer_id: Id del cliente
        :type customer_id: str
        :param card_token: Token de la tarjeta
        :type card_token: str
        :return: Tarjeta con su token
        :rtype: dict
        """
        response = {
                'id': card_token
            }
        return self.ok(response=response)

    def get(self, customer_id: str, card_id: str):
        r = requests.get('{}/usersite/{}/cardtokens'.format(self.url, customer_id), headers=self.headers)
        response = r.json()
        
        if 'tokens' not in response:
            return self.error(message=response['message'])
        
        cards = response['tokens']

        for card in cards:
            if card['token'] == card_id:
                return self.ok(response=_format(card, customer_id), status=r.status_code)
        return self.error(message='card not found')

    def list_all(self, customer_id: str):
        r = requests.get('{}/usersite/{}/cardtokens'.format(self.url, customer_id), headers=self.headers)
        response = r.json()
        if 'tokens' not in response:
            return self.error(message='customer not found')
        cards = response['tokens']
        return self.ok(response={'results': [_format(card, customer_id) for card in cards]}, status=r.status_code)
