from sirendb.models.siren import Siren
from sirendb.models.siren_model import SirenModel

pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


LIST_QUERY = '''
query listSirens($paginate: Paginate, $sort: SirenSortEnum, $filter: SirenFilter) {
  sirens(paginate: $paginate, sort: $sort, filter: $filter) {
    count
    pageInfo {
      hasNext
      lastCursor
    }
    items {
      active
      model {
        name
      }
      # locations {
      #   topographicLatitude
      #   topographicLongitude
      #   topographicZoom
      # }
    }
  }
}
'''


def test_list_siren(app, user_client, db):
    siren_model = SirenModel(name='3T22A')
    db.session.add(siren_model)
    db.session.commit()

    siren = Siren()
    siren.model_id = siren_model.id
    siren.active = True
    db.session.add(siren)
    db.session.commit()

    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listSirens',
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'sirens': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': ''
                },
                'items': [{
                    'active': True,
                    'model': {
                        'name': '3T22A',
                    },
                    # 'locations': []
                }]
            }
        }
    }
