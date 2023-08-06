import mercadopago
from iso8601 import parse_date
from bson import ObjectId

from ..MuviBase import MuviBase

card_brand_map = {
    # Credito
    'visa': 1,
    'diners': 8,
    'tarshop': 23,
    'naranja': 24,
    'pagofacil': 25,
    'rapipago': 26,
    'argencard': 30,
    'cencosud': 43,
    'cabal': 63,
    'amex': 65,
    'master': 104,
    # Debito
    'debvisa': 31,
    'debmaster': 105,
    'maestro': 106,
    'debcabal': 108
}

inverse_card_brand_map = {v: k for k, v in card_brand_map.items()}


def _format_card(response):
    return {
        'id': response['card']['id'],
        'card_type': response['payment_type_id'],
        'last_four_digits': response['card']['last_four_digits'],
        'cardholder': {
            'name': response['card']['cardholder']['name']
        },
        'expiration_month': response['card']['expiration_month'],
        'expiration_year': response['card']['expiration_year'],
    }


def _format(response):
    response['payment_method'] = response['payment_method_id']
    if response['payment_method_id'] in card_brand_map:
        response['payment_method_id'] = card_brand_map[response['payment_method_id']]

    fee_details = [{'type': d['type'], 'amount': d['amount']} for d in response['fee_details']]
    for f in [{'type': d['name'], 'amount': d['amounts']['original']} for d in response['charges_details']]:
        if f not in fee_details:
            fee_details.append(f)

    return {
        'id': response['id'],
        'transaction_amount': response['transaction_amount'],
        'date_created': parse_date(response['date_created']),
        'status': response['status'],
        'status_detail': response['status_detail'],
        'card': _format_card(response),
        'payment_day': parse_date(response['date_created']),
        'statement_descriptor': response['statement_descriptor'],
        'payment_method_id': response['payment_method_id'],
        'payment_method': response['payment_method'],
        'installments': response['installments'],
        'transaction_details': {
            'fee_details': fee_details,
            'net_received_amount': response['transaction_details']['net_received_amount']
        }
    }


class Payment(MuviBase):
    def __init__(self, processor: str, sdk: mercadopago.SDK, merchant_id: ObjectId):
        super().__init__(processor)
        self.sdk = sdk
        self.merchant_id = merchant_id

    def create(self, payment_data: dict):
        payment_data = payment_data.copy()
        merchant_id = str(self.merchant_id)
        notification_url = f"https://apisportclub.xyz/notificacion/mp?source_news=webhooks&merchant={merchant_id}"
        payment_data_mp = {
            "notification_url": notification_url,
            "transaction_amount": round(payment_data['transaction_amount'], 2),
            "token": payment_data['token'],
            "installments": 1,
        }

        optional_fields = [
            'additional_info',
            'description',
            'external_reference',
            'point_of_interaction',
            'installments',
            # 'payment_method_id',
            'application_fee',
            'notification_url',
            'binary_mode'
        ]
        for f in optional_fields:
            if f in payment_data:
                payment_data_mp[f] = payment_data[f]

        # if 'payment_method_id' in payment_data_mp and payment_data_mp['payment_method_id'] in inverse_card_brand_map:
        #     payment_data_mp['payment_method_id'] = inverse_card_brand_map[payment_data_mp['payment_method_id']]

        if 'payer' in payment_data:
            payment_data_mp["payer"] = {
                "first_name": payment_data['payer']["nombre"],
                "last_name": payment_data['payer']["apellido"],
                "address": None
            }
            if 'mercadopago_id' in payment_data['payer']:
                payment_data_mp['payer']['id'] = payment_data['payer']["mercadopago_id"]
            elif 'email' in payment_data['payer']:
                payment_data_mp['payer']['email'] = payment_data['payer']["email"]

        payment_response = self.sdk.payment().create(payment_data_mp)
        if payment_response['status'] < 400:
            return self.ok(response=_format(payment_response['response']), status=payment_response['status'])

        return self.error(response=payment_response['response'], status=payment_response['status'])

    def get(self, payment_id: int):
        payment_response = self.sdk.payment().get(payment_id)
        if payment_response['status'] < 400:
            return self.ok(response=payment_response['response'], status=payment_response['status'])

        return self.error(response=payment_response['response'], status=payment_response['status'])
