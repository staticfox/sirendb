from datetime import datetime

from freezegun import freeze_time
import pytest

from sirendb.models.siren import Siren
from sirendb.models.siren_model import SirenModel
from sirendb.models.siren_system import SirenSystem


pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


CREATE_QUERY = '''
fragment LocationProps on SirenLocation {
  satelliteLatitude
  satelliteLongitude
  satelliteZoom
  streetLatitude
  streetLongitude
  streetHeading
  streetPitch
  streetZoom
  installationTimestamp
  removalTimestamp
  siren {
    model {
      name
    }
  }
  system {
    name
  }
}

mutation createLocation($form: CreateSirenLocationInput!) {
  createSirenLocation(form: $form) {
    ok
    message
    sirenLocation {
      ... LocationProps
    }
  }
}
'''


@pytest.fixture(autouse=True)
def patch_imaging_config(app):
    if not app.config.get('BIN_DIR'):
        pytest.skip('missing BIN_DIR')

    if not app.config.get('GEO_BUILD_DIR'):
        pytest.skip('missing GEO_BUILD_DIR')


@freeze_time('2021-04-03T06:13:09.291212', as_kwarg='freezer')
def test_create_siren_location(app, user_client, db, **kwarg):
    print('')
    user, client = user_client

    # freezer = kwarg['freezer']
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

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': CREATE_QUERY,
            'operationName': 'createLocation',
            'variables': {
                'form': {
                    'satelliteLatitude': 33.9379329,
                    'satelliteLongitude': -117.275838,
                    'satelliteZoom': 142.0,
                    'streetLatitude': 40.432241,
                    'streetLongitude': -96.9300097,
                    'streetHeading': 93,
                    'streetPitch': 43.145,
                    'streetZoom': 41.4,
                    'installationTimestamp': None,
                    'removalTimestamp': None,
                    'sirenId': 1,
                    'systemId': 1,
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'createSirenLocation': {
                'message': '',
                'ok': True,
                'sirenLocation': {
                    'satelliteLatitude': 33.9379329,
                    'satelliteLongitude': -117.275838,
                    'satelliteZoom': 142.0,
                    'streetLatitude': 40.432241,
                    'streetLongitude': -96.9300097,
                    'streetHeading': 93,
                    'streetPitch': 43.145,
                    'streetZoom': 41.4,
                    'installationTimestamp': None,
                    'removalTimestamp': None,
                    'siren': {
                        'model': {
                            'name': '3T22A'
                        }
                    },
                    'system': {
                        'name': 'Test Siren System',
                    },
                },
            }
        }
    }
