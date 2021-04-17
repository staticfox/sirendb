from datetime import datetime

from freezegun import freeze_time
import pytest

from sirendb.models.siren import Siren
from sirendb.models.siren_location import SirenLocation
from sirendb.models.siren_manufacturer import SirenManufacturer
from sirendb.models.siren_media import (
    SirenMediaType,
    SirenMedia,
)
from sirendb.models.siren_model import SirenModel
from sirendb.models.siren_system import SirenSystem

pytest_plugins = (
    'tests.fixtures',
    'tests.v1.auth.fixtures',
)


LIST_QUERY = '''
fragment LocationProps on SirenLocation {
  media {
    downloadUrl
    mediaType
    mimetype
    kilobytes
  }
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
      manufacturer {
        name
      }
    }
  }
  system {
    name
  }
}

query listLocations($paginate: Paginate, $sort: SirenLocationSortEnum, $filter: SirenLocationFilter) {
  sirenLocations(paginate: $paginate, sort: $sort, filter: $filter) {
    count
    pageInfo {
      hasNext
      lastCursor
    }
    items {
      ... LocationProps
    }
  }
}
'''


@pytest.fixture(autouse=True)
def patch_store_config(app):
    app.config['IMAGE_STORE_BASE_URL'] = 'http://localhost:5000/media'
    app.config['IMAGE_STORE_TYPE'] = 'testing'
    app.config['IMAGE_STORE_PATH'] = '/images'

    yield

    del app.config['IMAGE_STORE_BASE_URL']
    del app.config['IMAGE_STORE_TYPE']
    del app.config['IMAGE_STORE_PATH']


@freeze_time('2021-04-03T06:13:09.291212')
def test_list_siren_locations(app, user_client, db):
    siren_system = SirenSystem(name='Test Siren System')
    siren_system.created_timestamp = datetime.utcnow()
    db.session.add(siren_system)
    db.session.commit()

    siren_manufacturer = SirenManufacturer(name='Federal Signal')
    siren_manufacturer.created_timestamp = datetime.utcnow()
    siren_manufacturer.founded_timestamp = datetime.utcnow()
    db.session.add(siren_manufacturer)
    db.session.commit()

    siren_model = SirenModel(name='3T22A')
    siren_model.created_timestamp = datetime.utcnow()
    siren_model.manufacturer_id = siren_manufacturer.id
    db.session.add(siren_model)
    db.session.commit()

    siren = Siren()
    siren.model_id = siren_model.id
    siren.active = True
    db.session.add(siren)
    db.session.commit()

    siren_location = SirenLocation()
    siren_location.installation_timestamp = datetime.utcnow()
    siren_location.removal_timestamp = datetime.utcnow()
    siren_location.satellite_latitude = 0.0
    siren_location.satellite_longitude = 0.0
    siren_location.satellite_zoom = 0.0
    siren_location.street_latitude = 0.0
    siren_location.street_longitude = 0.0
    siren_location.street_heading = 0.0
    siren_location.street_pitch = 0.0
    siren_location.street_zoom = 0.0
    siren_location.siren_id = siren.id
    siren_location.system_id = siren_system.id
    db.session.add(siren_location)
    db.session.commit()

    siren_media = SirenMedia(
        media_type=SirenMediaType.STREET_IMAGE,
        mimetype='image/png',
        kilobytes=12.432,
        location_id=siren_location.id,
        filename='test.png',
        filesystem_uri='filesystem://./images/test.png',
    )
    db.session.add(siren_media)
    db.session.commit()

    user, client = user_client

    response = client.post(
        '/api/v1/graphql',
        json={
            'query': LIST_QUERY,
            'operationName': 'listLocations',
        }
    )
    assert response.status_code == 200
    import json
    print(json.dumps(response.json, indent=4))
    assert response.json == {
        'data': {
            'sirenLocations': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': ''
                },
                'items': [{
                    'installationTimestamp': '2021-04-03T06:13:09.291212',
                    'media': [{
                        'downloadUrl': 'http://localhost:5000/media/test.png',
                        'kilobytes': 12.432,
                        'mediaType': 'STREET_IMAGE',
                        'mimetype': 'image/png',
                    }],
                    'removalTimestamp': '2021-04-03T06:13:09.291212',
                    'satelliteLatitude': 0.0,
                    'satelliteLongitude': 0.0,
                    'satelliteZoom': 0.0,
                    'siren': {
                        'model': {
                            'name': '3T22A',
                            'manufacturer': {
                                'name': 'Federal Signal',
                            },
                        },
                    },
                    'streetHeading': 0.0,
                    'streetLatitude': 0.0,
                    'streetLongitude': 0.0,
                    'streetPitch': 0.0,
                    'streetZoom': 0.0,
                    'system': {
                        'name': 'Test Siren System',
                    },
                }]
            }
        }
    }
