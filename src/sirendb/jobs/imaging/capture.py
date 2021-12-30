import logging
from typing import Optional

from flask import current_app

from sirendb.core.db import db
from sirendb.core.rq import rq
from sirendb.models.siren_location import (
    SatelliteCoordinates,
    StreetCoordinates,
)
from sirendb.models.siren_media import (
    SirenMedia,
    SirenMediaType,
)
from sirendb.lib.storage import storage

from .chrome import Chrome
from .nginx import Nginx

log = logging.getLogger('sirendb.imaging.capture')


def _capture_image(http_path: str) -> Optional[bytes]:
    bin_dir = current_app.config.get('BIN_DIR')
    if not bin_dir:
        log.error('_capture_image failed: missing BIN_DIR')
        return None

    geo_dir = current_app.config.get('GEO_BUILD_DIR')
    if not geo_dir:
        log.error('_capture_image failed: missing GEO_BUILD_DIR')
        return None

    with Nginx(bin_dir=bin_dir, geo_dir=geo_dir) as netloc:
        if not netloc:
            return None

        with Chrome(bin_dir=bin_dir) as chrome:
            local_url = f'http://{netloc}/{http_path}'
            screenshot = chrome.capture_screenshot(local_url)
            log.debug('captured screenshot, stopping chrome...')

        log.debug('stopped chrome, stopping nginx...')

    log.debug('stopped nginx')

    return screenshot


@rq.job
def capture_satellite_image(location_id: int, coordinates: SatelliteCoordinates) -> None:
    http_path = 'sat?lat={lat}&lng={lng}&zoom={zoom}'.format(
        lat=coordinates.latitude,
        lng=coordinates.longitude,
        zoom=coordinates.zoom,
    )
    log.info(f'capturing screenshot for {location_id}')
    screenshot = _capture_image(http_path)
    if not screenshot:
        return

    media = SirenMedia(
        media_type=SirenMediaType.SATELLITE_IMAGE,
        mimetype='image/png',
        kilobytes=(len(screenshot) / 1024),
        location_id=location_id,
    )

    save_result = storage.save(screenshot, 'png', 'image/png')
    if save_result:
        media.filename = save_result.filesystem_key
        media.filesystem_uri = save_result.filesystem_uri

    db.session.add(media)
    db.session.commit()


@rq.job
def capture_streetview_image(location_id: int, coordinates: StreetCoordinates) -> None:
    http_path = '?lat={lat}&lng={lng}&heading={heading}&pitch={pitch}&zoom={zoom}'.format(
        lat=coordinates.latitude,
        lng=coordinates.longitude,
        heading=coordinates.heading,
        pitch=coordinates.pitch,
        zoom=coordinates.zoom,
    )
    log.info(f'capturing screenshot for {location_id}')
    screenshot = _capture_image(http_path)
    if not screenshot:
        return

    media = SirenMedia(
        media_type=SirenMediaType.STREET_IMAGE,
        mimetype='image/png',
        kilobytes=(len(screenshot) / 1024),
        location_id=location_id,
    )

    save_result = storage.save(screenshot, 'png', 'image/png')
    if save_result:
        media.filename = save_result.filesystem_key
        media.filesystem_uri = save_result.filesystem_uri

    db.session.add(media)
    db.session.commit()
