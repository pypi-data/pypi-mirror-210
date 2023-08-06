import mercadopago

from ..MuviBase import MuviBase


def _format(response: dict) -> dict:
    return {
        'email': response['email'],
        'first_name': response['first_name'],
        'last_name': response['last_name'],
        'id': response['id']
    }


class Customer(MuviBase):
    def __init__(self, processor: str, sdk: mercadopago.SDK):
        super().__init__(processor)
        self.sdk = sdk

    def _validate_client(self, client: dict) -> dict:
        fields = ['nombre', 'apellido', 'documento', 'email', 'domicilio']
        for f in fields:
            if f not in client:
                return self.error(message='{} field is missing'.format(f))

        for f in ['calle', 'altura']:
            if f not in client['domicilio']:
                return self.error(message='domicilio.{} field is missing'.format(f))

        return self.ok(response=client)

    def create(self, client: dict) -> dict:
        """

        :param client: Diccionario del cliente
        nombre, apellido, documento, email, domicilio son obligatorios
        :return:
        """
        # Check para el client y evitar errores
        client = client.copy()
        r = self._validate_client(client)
        if r['status'] >= 400:
            return r

        customer_response = self.sdk.customer().search(filters={'email': client['email']})
        if len(customer_response['response']['results']) > 0:
            return self.ok(response=_format(customer_response['response']['results'][0]))

        try:
            street_number = int(client['domicilio']['altura'])
        except:
            street_number = 1

        mp_customer_data = {
            'email': client['email'],
            'first_name': client['nombre'],
            'last_name': client['apellido'],
            'phone': {
                'area_code': None,
                'number': client['celular']
            },
            'identification': {
                'type': 'DNI',
                'number': client['documento']
            },  # ! Tipo de identificacion hardcodeado
            'address': {
                'street_name': client['domicilio']['calle'],
                'street_number': street_number,
            }
        }
        mp_response = self.sdk.customer().create(mp_customer_data)
        if mp_response['status'] < 400:
            return self.ok(response=_format(mp_response['response']), status=mp_response['status'])

        return self.error(response=mp_response['response'], status=mp_response['status'])

    def get(self, customer_id: str):
        mp_response = self.sdk.customer().get(customer_id)
        if mp_response['status'] < 400:
            customer = mp_response['response']
            return self.ok(response=_format(customer), status=mp_response['status'])

        return self.error(response=mp_response['response'], status=mp_response['status'])

    def search(self, filters: dict):
        mp_response = self.sdk.customer().search(filters)
        if mp_response['status'] < 400:
            return self.ok(response=mp_response['response'], status=mp_response['status'])

        return self.error(response=mp_response['response'], status=mp_response['status'])
