from datetime import datetime

from sirendb.models.siren import Siren
from sirendb.models.siren_location import SirenLocation
from sirendb.models.siren_model import SirenModel
from sirendb.models.siren_system import SirenSystem

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
      locations {
        satelliteLatitude
        satelliteLongitude
        satelliteZoom
        siren {
          model {
            name
          }
        }
        system {
          name
        }
      }
    }
  }
}
'''


def test_list_siren(app, user_client, db):
    siren_model = SirenModel(name='3T22A')
    siren_model.created_timestamp = datetime.utcnow()
    db.session.add(siren_model)
    db.session.commit()

    siren = Siren()
    siren.model_id = siren_model.id
    siren.active = True
    db.session.add(siren)
    db.session.commit()

    siren_system = SirenSystem(name='Test Siren System')
    siren_system.created_timestamp = datetime.utcnow()
    db.session.add(siren_system)
    db.session.commit()

    location = SirenLocation(
        satellite_latitude=33.9379329,
        satellite_longitude=-117.275838,
        satellite_zoom=142.0,
        siren_id=siren.id,
        system_id=siren_system.id,
    )
    db.session.add(location)
    db.session.commit()

    # Ensure there is no floating point truncation
    assert location.satellite_latitude == 33.9379329
    assert location.satellite_longitude == -117.275838
    assert location.satellite_zoom == 142.0

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
                    'locations': [{
                        'satelliteLatitude': 33.9379329,
                        'satelliteLongitude': -117.275838,
                        'satelliteZoom': 142.0,
                        'siren': {
                            'model': {
                                'name': '3T22A'
                            }
                        },
                        'system': {
                            'name': 'Test Siren System',
                        },
                    }],
                    'model': {
                        'name': '3T22A',
                    }
                }]
            }
        }
    }
