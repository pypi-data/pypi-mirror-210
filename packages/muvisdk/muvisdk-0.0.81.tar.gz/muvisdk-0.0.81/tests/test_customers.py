import pytest
import random
import string

from muvisdk.SDK import SDK

# Credenciales de test
merchant = {
    '_id': '012345',
    'name': 'Un Merchant de test',
    'credentials': {
        'mercadopago': {
            'access_token': 'TEST-7306398834844755-071810-f54f60f3cb6c0da2bb76c3201711f7fa-1161352268'
        },
        'decidir': {
            'public_key': 'fEvHoakBPLO2vMkFHpCNwt5H7F1albtY',
            'access_token': '7UEr3kX4paS91dXwZw2H4avATuN6jNSt'
        }
    }
}


def mercadopago_params():
    merchant['credentials']['preferred_processor'] = 'mercadopago'
    return (
        SDK(merchant)
    )


def decidir_params():
    merchant['credentials']['preferred_processor'] = 'decidir'
    return (
        SDK(merchant)
    )


client = {
    'email': 'francisco006@muvinai.com',
    'nombre': 'Francisco',
    'apellido': 'Viñas',
    'celular': '11111111',
    'documento': '22222222',
    'domicilio': {
        'altura': '123',
        'calle': 'Calle Falsa'
    }
}


def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def random_email():
    return '{}@{}.com'.format(random_string(10), random_string(5))


@pytest.mark.parametrize('sdk', [mercadopago_params(), decidir_params()])
class TestCustomer:
    def test_get_customer_not_found(self, sdk):
        r = sdk.customer().get('128763198273698172')
        assert r['status'] == 'error'

    def test_create_and_get_customer(self, sdk):
        new_client = client.copy()
        new_client['email'] = random_email()
        r = sdk.customer().create(new_client)
        assert r['status'] == 'ok'
        create_response = r['response']
        assert create_response['email'] == new_client['email']
        assert create_response['first_name'] == new_client['nombre']
        assert create_response['last_name'] == new_client['apellido']
        assert create_response['id'] is not None

        r = sdk.customer().get(create_response['id'])
        assert r['status'] == 'ok'
        get_response = r['response']
        assert get_response['email'] == new_client['email']
        assert get_response['first_name'] == new_client['nombre']
        assert get_response['last_name'] == new_client['apellido']
        assert get_response['id'] == create_response['id']
