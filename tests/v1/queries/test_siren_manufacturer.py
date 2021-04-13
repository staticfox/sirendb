from datetime import datetime

from sirendb.models.siren_manufacturer import SirenManufacturer

pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


LIST_QUERY = '''
query listManufacturers($paginate: Paginate, $sort: SirenManufacturerSortEnum, $filter: SirenManufacturerFilter) {
  sirenManufacturers(paginate: $paginate, sort: $sort, filter: $filter) {
    count
    pageInfo {
      hasNext
      lastCursor
    }
    items {
      name
    }
  }
}
'''


def test_list_siren_manufacturer(app, user_client, db):
    siren_manufacturer = SirenManufacturer(name='Test Siren Manufacturer')
    siren_manufacturer.created_timestamp = datetime.utcnow()
    siren_manufacturer.founded_timestamp = datetime.utcnow()
    db.session.add(siren_manufacturer)
    db.session.commit()

    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listManufacturers',
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirenManufacturers': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': ''
                },
                'items': [{
                    'name': 'Test Siren Manufacturer'
                }]
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listManufacturers',
            'variables': {
                'paginate': {
                    'first': 0
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirenManufacturers': {
                'count': 0,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': ''
                },
                'items': []
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listManufacturers',
            'variables': {
                'sort': 'ID_ASC'
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirenManufacturers': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': ''
                },
                'items': [{
                    'name': 'Test Siren Manufacturer'
                }]
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listManufacturers',
            'variables': {
                'sort': 'ID_ASC',
                'filter': {
                    'name': 'prod*'
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirenManufacturers': {
                'count': 0,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': ''
                },
                'items': []
            }
        }
    }
