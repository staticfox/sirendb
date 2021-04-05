from freezegun import freeze_time


pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


CREATE_QUERY = '''
mutation createSystem($form: CreateSirenSystemInput!) {
  createSirenSystem(form: $form) {
    ok
    message
    sirenSystem {
      createdTimestamp
      name
    }
  }
}
'''


@freeze_time('2021-04-03T06:13:09.291212')
def test_create_siren_system(app, user_client, db):
    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': CREATE_QUERY,
            'operationName': 'createSystem',
            'variables': {
                'form': {
                    'name': 'Test System Name',
                    'state': 'Test City',
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'createSirenSystem': {
                'message': '',
                'ok': True,
                'sirenSystem': {
                    'createdTimestamp': '2021-04-03T06:13:09.291212',
                    'name': 'Test System Name',
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
            'operationName': 'createSystem',
            'variables': {
                'form': {
                    'name': 'Test System Name' + ('#' * 100) + '@@@@',
                    'state': 'Test City',
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': None,
        'errors': [{
            'locations': [{
                'column': 23,
                'line': 2
            }],
            'message': (
                "Variable '$form' got invalid value 'Test System "
                "Name########################################################################"
                "############################@@@@' at 'form.name'; Expected type 'LimitedString'. "
            ),
            'path': None,
        }]
    }
