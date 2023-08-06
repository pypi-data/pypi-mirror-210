import requests
import time
import pytz
from iso8601 import parse_date
from ..MuviBase import MuviBase

map_errors = {
    1:"pedir autorizacion",
    2: "pedir autorizacion",
    3: "comercio invalido",
    4: "capturar tarjeta",
    5: "denegada",
    7: "retenga y llame",
    8: "ingreso manual incorrecto",
    12: "transac. invalida",
    13: "monto invalido",
    14: "tarjeta invalida",
    19: "auto approve in receivepayment",
    25: "no existe original",
    28: "servicio no disponible",
    30: "error en formato",
    31: "the parameter must be specified.",
    38: "excede ing.de pin",
    39: "ingreso manual incorrecto",
    43: "retener tarjeta",
    45: "no opera en cuotas",
    46: "tarjeta no vigente",
    47: "pin requerido",
    48: "excede max. cuotas",
    49: "error fecha vencim.",
    50: "entrega supera limite",
    51: "fondos insuficientes",
    53: "cuenta inexistente",
    54: "tarjeta vencida",
    55: "pin incorrecto",
    56: "tarj. no habilitada",
    57: "trans. no permitida",
    58: "servicio invalido",
    61: "excede limite",
    65: "excede lim. tarjeta",
    76: "llamar al emisor",
    77: "error plan/cuotas",
    89: "terminal invalida",
    91: "emisor fuera linea",
    94: "nro. sec. duplicad",
    95: "re-transmitiendo",
    96: "error en sistema",
    97: "error en sistema host",
    98: "ver rechazo en ticket",
}
arg_tz = pytz.timezone('America/Buenos_Aires')

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
    if 'card' in response:
        return {
            'id': response['card']['id'],
            'card_type': 'not_found',
            'last_four_digits': response['card']['last_four_digits'],
            'cardholder': {
                'name': response['card']['cardholder']['name']
            },
            'expiration_month': response['card']['expiration_month'],
            'expiration_year': response['card']['expiration_year'],
        }
        
    if 'card_data' in response and 'tokens' not in response['card_data']:
        return {
            'id': '',
            'card_type': '',
            'last_four_digits': response['card_data']['card_number'][-4:],
            'cardholder': {
                'name': response['card_data']['card_holder']['name']
            },
            'expiration_month': '',
            'expiration_year': '',
        }
    
    return {
        'id': '',
        'card_type': '',
        'last_four_digits': '',
        'cardholder': {
            'name': ''
        },
        'expiration_month': '',
        'expiration_year': '',
    }


def _format(response):
    if response['status'] in ['accredited', 'approved']:
        response['status'] = 'approved'
        response['status_detail'] = 'accredited'
    elif response['status'] == 'rejected':
        id_error = int(response['status_details']['error']['reason']['id'])
        if id_error in map_errors:
            response['status_detail'] = map_errors[id_error]
        else:
            response['status_detail'] = 'error desconocido'
    elif response['status'] == 'annulled' or response['status'] == 'refunded':
        response['status'] = 'refunded'
        response['status_detail'] = 'refunded'
    date = parse_date(response['date']).astimezone(arg_tz)
    
    response['payment_method'] = response['payment_method_id']
    if response['payment_method_id'] in inverse_card_brand_map:
        response['payment_method'] = inverse_card_brand_map[response['payment_method_id']]
    
    result = {
        'id': int(response['site_transaction_id']), # Generado por el sdk
        'payment_id': response['id'],               # Genereador por decidir
        'transaction_amount': response['amount'] / 100,
        'date_created': date,
        'status': response['status'],
        'status_detail': response['status_detail'],
        'card': {'id': response['customer_token']} if 'customer_token' in response else _format_card(response),
        'payment_day': date,
        'statement_descriptor': response['establishment_name'],
        'payment_method_id': response['payment_method_id'],
        'payment_method': response['payment_method'],
        'installments': response['installments'],
    }
    return result


class Payment(MuviBase):
    def __init__(self, processor: str, url: str, private_key: str, public_key: str, merchant_name: str, site_id: str,
                 site_id_cadena_con_cvv: str, site_id_cadena_sin_cvv: str, marketplace: bool):
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

    def create(self, payment_data: dict, con_cvv: bool = False):
        site_transaction_id = int(time.time()*1e2) # Se genera un payment_id para decidir
        total_amount = round(payment_data['transaction_amount'], 2) * 100  # se multiplica por 100; no acepta decimales
        installments = payment_data['installments'] if 'installments' in payment_data else 1
        
        if con_cvv:
            site_id = self.site_id_cadena_con_cvv
        else:
            if self.marketplace:
                site_id = self.site_id_cadena_sin_cvv
            else:
                site_id = self.site_id

        body = {
            'customer': {
                'id': payment_data['payer']['decidir_id'],
                'email': payment_data['payer']['email']
            },
            'site_id': site_id,
            'site_transaction_id': str(site_transaction_id),
            'token': payment_data['token'],
            'payment_method_id': payment_data['payment_method_id'],
            'bin': payment_data['bin'],     # primeros 6 digitos de la tarjeta
            'currency': 'ARS',
            'payment_type': 'single',
            'establishment_name': self.merchant_name if 'establishment_name' not in payment_data else payment_data['establishment_name'],
            'sub_payments': [],
            'amount': total_amount, # En cualquier tipo de payment
            'installments': installments,
        }
        if 'application_fee' in payment_data and self.marketplace:
            application_fee = round(payment_data['application_fee'], 2) * 100
            body['payment_type'] = 'distributed'
            del body['site_id']
            body['sub_payments'] = [
                {
                    'site_id': self.site_id_cadena_sin_cvv,
                    'installments': installments,
                    'amount': application_fee
                }, {
                    'site_id': self.site_id,
                    'installments': installments,
                    'amount': total_amount - application_fee
                }
            ]
        elif 'application_fee' in payment_data and not self.marketplace:
            # No se puede hacer split si marketplace = False
            return self.error(message='application_fee_not_expected')

        # Si viene informacion adicional
        additional_information = [
            'establishment_name'
        ]
        for item in additional_information:
            if item in payment_data.keys():
                body[item] = payment_data[item]

        # Se genera la request
        r = requests.post(self.url + '/payments', headers=self.headers, json=body)
        response = r.json()
        if 'status' in response and 'site_transaction_id' in response:
            if 'card' in payment_data:
                response['card'] = payment_data['card']
            return self.ok(response=_format(response))
        return self.error(response=response, status=r.status_code)

    def get(self, payment_id):
        filters = {
            'siteOperationId': int(payment_id),
            'expand': 'card_data'
        }
        r = requests.get(self.url + '/payments', params=filters, headers=self.headers)
        list_results = r.json()['results']
        if len(list_results) == 1:
            return self.ok(response=_format(list_results[0]), status=r.status_code)
        else:
            return self.error(message='error_pago_no_encontrado', status=r.status_code)

    def search(self, filters: dict) -> dict:
        # El filter puede ser:
        # offset
        # pageSize
        # siteOperationId
        # merchantId
        # dateFrom
        # dateTo
        # site
        r = requests.get(self.url + '/payments', params=filters, headers=self.headers)
        response = r.json()
        response['results'] = [_format(r) for r in response['results']]
        return self.ok(response=response, status=r.status_code)

    def get_payment_methods(self):
        r = requests.get(self.url + '/payment-methods/1', headers=self.headers)
        return self.ok(response=r.json(), status=r.status_code)
