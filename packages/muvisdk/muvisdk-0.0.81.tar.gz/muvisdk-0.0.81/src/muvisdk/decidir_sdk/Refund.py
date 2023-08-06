import requests
import json

from ..MuviBase import MuviBase
from .Payment import Payment


class Refund(MuviBase):
    def __init__(self,
                 processor: str,
                 url: str,
                 private_key: str,
                 public_key: str,
                 merchant_name: str,
                 site_id: str,
                 site_id_cadena_con_cvv: str, 
                 site_id_cadena_sin_cvv: str,
                 marketplace: bool):
        super().__init__(processor)
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.merchant_name = merchant_name
        self.site_id = site_id
        self.site_id_cadena_con_cvv = site_id_cadena_con_cvv
        self.site_id_cadena_sin_cvv = site_id_cadena_sin_cvv
        self.marketplace = marketplace
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, payment_id: str, amount: float = None) -> dict:
        # Busco el pago
        payment = Payment(self.processor, self.url, self.private_key, self.public_key, self.merchant_name, self.site_id, self.site_id_cadena_con_cvv, self.site_id_cadena_sin_cvv, self.marketplace)

        response_get = payment.get(payment_id)
        if response_get['status'] < 400:
            payment_id_decidir = response_get['response']['payment_id']
        else:
            return {'status':404,'response':'payment_not_found'}

        data = {
            'amount': round(amount, 2) * 100 if amount else amount
        }
        r = requests.post(self.url + f'/payments/{payment_id_decidir}/refunds', headers=self.headers, data=json.dumps(data))
        if r.status_code < 400:
            response = r.json()
            response['amount'] = response['amount'] / 100
            return self.ok(response=response, status=r.status_code)
        return self.error(response=r.json(), status=r.status_code)
