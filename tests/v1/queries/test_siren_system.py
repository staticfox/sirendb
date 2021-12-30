from sirendb.models.siren_system import SirenSystem

pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


LIST_QUERY = '''
query listSystems($paginate: Paginate, $sort: SirenSystemSortEnum, $filter: SirenSystemFilter) {
  sirenSystems(paginate: $paginate, sort: $sort, filter: $filter) {
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


def test_list_siren_system(app, user_client, db):
    user, client = user_client

    siren_system = SirenSystem(name='Test Siren System')
    siren_system.created_by_id = user.id
    db.session.add(siren_system)
    db.session.commit()

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listSystems',
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirenSystems': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': str(siren_system.id),
                },
                'items': [{
                    'name': 'Test Siren System'
                }]
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listSystems',
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
            'sirenSystems': {
                'count': 0,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': None,
                },
                'items': []
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listSystems',
            'variables': {
                'sort': 'ID_ASC'
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirenSystems': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': str(siren_system.id),
                },
                'items': [{
                    'name': 'Test Siren System'
                }]
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listSystems',
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
            'sirenSystems': {
                'count': 0,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': None,
                },
                'items': []
            }
        }
    }
