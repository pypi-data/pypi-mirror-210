import mercadopago
from .Customer import Customer
from .Card import Card
from .CardToken import CardToken
from .Payment import Payment
from .Refund import Refund


class MercadoPagoSDK:
    def __init__(self, merchant: dict, marketplace: bool = False):
        mercadopago_model = 'mp_marketplace' if marketplace else 'mercadopago'

        active = merchant['credentials'][mercadopago_model]['active']
        access_token = merchant['credentials'][mercadopago_model]['access_token'] if active else None

        self.sdk = mercadopago.SDK(access_token) if active else None
        self.merchant_id = merchant['_id']
        self.merchant_name = merchant['name']
        self.processor = 'mercadopago'

    def customer(self):
        return Customer(self.processor, self.sdk)
    
    def card(self):
        return Card(self.processor, self.sdk)

    def card_token(self):
        return CardToken(self.processor, self.sdk)
    
    def payment(self):
        return Payment(self.processor, self.sdk, self.merchant_id)

    def refund(self):
        return Refund(self.processor, self.sdk)

    def ok(self):
        return self.sdk is not None
