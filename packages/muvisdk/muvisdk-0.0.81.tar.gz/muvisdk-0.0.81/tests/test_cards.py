import pytest

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
        SDK(merchant),
        '1163536800-CLBbg46pSRduJi',  # customer_id
        '1658246890412',  # card_id
        '9734d788ac10cbc7bc8b1a73060575b8'  # card_token
    )


def decidir_params():
    merchant['credentials']['preferred_processor'] = 'decidir'
    return (
        SDK(merchant),
        '588b945d-9333-4a8c-af76-95412eb02913',  # customer_id
        '40973830e2f4f625f96705fa7b60c446d951bc4c518ebea5af2d4225b43bf3d6',  # card_id
        'caf63949-f149-445f-bdb0-f838a2f9691e'  # card_token
    )


@pytest.mark.parametrize(
    ('sdk', 'customer_id', 'card_id', 'card_token'),
    [
        mercadopago_params(),
        decidir_params()
    ]
)
class TestCard:
    def test_create_card(self, sdk, customer_id, card_id, card_token):
        r = sdk.card().create(customer_id, card_token)
        assert r['status'] == 'ok'
        assert r['response']['id'] is not None

    def test_get_card_found(self, sdk, customer_id, card_id, card_token):
        r = sdk.card().get(customer_id, card_id)
        assert r['status'] == 'ok'
        assert r['response']['id'] is not None
        assert r['response']['id'] == card_id
