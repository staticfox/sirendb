from datetime import datetime

from freezegun import freeze_time

from sirendb.models.siren_manufacturer import SirenManufacturer

pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


CREATE_QUERY = '''
mutation createModel($form: CreateSirenModelInput!) {
  createSirenModel(form: $form) {
    ok
    message
    sirenModel {
      createdTimestamp
      info
      name
      manufacturer {
        name
      }
      manufacturerId
    }
  }
}
'''


@freeze_time('2021-04-03T06:13:09.291212')
def test_create_siren_model_with_unknown_manufacturer_id(app, user_client, db):
    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': CREATE_QUERY,
            'operationName': 'createModel',
            'variables': {
                'form': {
                    'name': 'Test Model Name',
                    'info': 'unknown manufacturer',
                    'manufacturerId': 3,
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'createSirenModel': {
                'message': 'Unknown manufacturerId.',
                'ok': False,
                'sirenModel': None,
            }
        }
    }


@freeze_time('2021-04-03T06:13:09.291212')
def test_create_siren_model(app, user_client, db):
    siren_manufacturer = SirenManufacturer(name='Test Siren Manufacturer')
    siren_manufacturer.created_timestamp = datetime.utcnow()
    siren_manufacturer.founded_timestamp = datetime.utcnow()
    db.session.add(siren_manufacturer)
    db.session.commit()

    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': CREATE_QUERY,
            'operationName': 'createModel',
            'variables': {
                'form': {
                    'name': 'Test Model Name',
                    'info': 'unknown manufacturer',
                    'manufacturerId': siren_manufacturer.id,
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'createSirenModel': {
                'message': '',
                'ok': True,
                'sirenModel': {
                    'createdTimestamp': '2021-04-03T06:13:09.291212',
                    'info': 'unknown manufacturer',
                    'manufacturer': {
                        'name': 'Test Siren Manufacturer'
                    },
                    'manufacturerId': siren_manufacturer.id,
                    'name': 'Test Model Name',
                },
            }
        }
    }


@freeze_time('2021-04-03T06:13:09.291212')
def test_name_exceeds_db_field_size(app, user_client, db):
    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': CREATE_QUERY,
            'operationName': 'createModel',
            'variables': {
                'form': {
                    'name': 'Test Model Name' + ('#' * 100) + '@@@@',
                    'info': 'unknown manufacturer',
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': None,
        'errors': [{
            'locations': [{
                'column': 22,
                'line': 2
            }],
            'message': (
                "Variable '$form' got invalid value 'Test Model "
                "Name########################################################################"
                "############################@@@@' at 'form.name'; Expected type 'LimitedString'. "
            ),
            'path': None,
        }]
    }
