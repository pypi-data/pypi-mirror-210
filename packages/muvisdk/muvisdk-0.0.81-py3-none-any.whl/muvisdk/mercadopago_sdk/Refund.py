import mercadopago

from ..MuviBase import MuviBase


class Refund(MuviBase):
    def __init__(self, processor: str, sdk: mercadopago.SDK):
        super().__init__(processor)
        self.sdk = sdk

    def create(self, payment_id: str, amount: float = None):
        refund_data = {
            "amount": amount
        }
        refund_response = self.sdk.refund().create(payment_id, refund_data)
        if refund_response['status'] < 400:
            return self.ok(response=refund_response['response'], status=refund_response['status'])
        else:
            return self.error(response=refund_response['response'], status=refund_response['status'])
