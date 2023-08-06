from .Card import Card
from .CardToken import CardToken
from .Customer import Customer
from .Payment import Payment
from .Refund import Refund


class DecidirSDK:
    def __init__(
        self,
        merchant: dict,
        merchant_cadena: dict,
        marketplace: bool = False,
        test: bool = True,
        force: bool = False
    ):
        if (decidir := merchant.get('credentials', {}).get('decidir', None)):
            if not decidir.get('site_id', None):
                self.private_key = None
                return
            
            if not force:
                if not decidir.get('active', False):
                    self.private_key = None
                    return
        
        credentials_cadena = merchant_cadena.get('credentials', {}).get('decidir', {})
        credentials_local = merchant.get('credentials', {}).get('decidir', {})

        environment = 'developers' if test else 'live'
        self.url = f'https://{environment}.decidir.com/api/v2'

        self.private_key = credentials_cadena.get('access_token')
        self.public_key = credentials_cadena.get('public_key')

        self.merchant_name = merchant.get('name')

        self.site_id = credentials_local.get('site_id')
        self.site_id_cadena_con_cvv = credentials_cadena.get('site_id_con_cvv')
        self.site_id_cadena_sin_cvv = credentials_cadena.get('site_id')

        self.processor = 'decidir'
        self.marketplace = marketplace

    def customer(self):
        return Customer(self.processor, self.url, self.private_key, self.public_key)
    
    def card(self):
        return Card(self.processor, self.url, self.private_key, self.public_key)

    def card_token(self):
        return CardToken(self.processor, self.url, self.private_key, self.public_key)

    def payment(self):
        return Payment(
            self.processor,
            self.url,
            self.private_key,
            self.public_key,
            self.merchant_name,
            self.site_id,
            self.site_id_cadena_con_cvv,
            self.site_id_cadena_sin_cvv,
            self.marketplace
        )

    def refund(self):
        return Refund(
            self.processor,
            self.url,
            self.private_key,
            self.public_key,
            self.merchant_name,
            self.site_id,
            self.site_id_cadena_con_cvv,
            self.site_id_cadena_sin_cvv,
            self.marketplace
        )

    def ok(self):
        return self.private_key is not None
