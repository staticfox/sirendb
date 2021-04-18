from datetime import datetime

from freezegun import freeze_time

from sirendb.models.siren import Siren
from sirendb.models.siren_model import SirenModel
from sirendb.models.siren_system import SirenSystem

pytest_plugins = (
    'tests.fixtures',
    'tests.jobs.imaging.fixtures',
    'tests.v1.auth.fixtures',
)


CREATE_QUERY = '''
fragment LocationProps on SirenLocation {
  media {
    downloadUrl
    mediaType
    mimetype
  }
  # mapCoordinates { ... }
  satelliteLatitude
  satelliteLongitude
  satelliteZoom
  streetLatitude
  streetLongitude
  streetHeading
  streetPitch
  streetZoom
  # ... end mapCoordinates
  # address { ... }
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


def test_create_siren_location(app, user_client, db):
    with freeze_time('2021-04-03T06:13:09.291212'):
        user, client = user_client

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

    response_json = dict(response.json)
    media = response_json['data']['createSirenLocation']['sirenLocation'].pop('media')

    assert len(media) == 2
    media_types = {'SATELLITE_IMAGE', 'STREET_IMAGE'}
    for item in media:
        assert item['downloadUrl'] is not None
        media_types.remove(item['mediaType'])
        assert item['mimetype'] == 'image/png'
    assert not media_types

    assert response_json == {
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
