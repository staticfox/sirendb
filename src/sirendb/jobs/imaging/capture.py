import logging
from pathlib import Path
import secrets
import time

from flask import current_app

from sirendb.core.rq import rq
from sirendb.models.siren_location import (
    SatelliteCoordinates,
    StreetCoordinates,
)

from .chrome import Chrome
from .nginx import Nginx

log = logging.getLogger('sirendb.imaging.capture')


def _capture_image(http_path: str) -> Path:
    bin_dir = current_app.config.get('BIN_DIR')
    if not bin_dir:
        log.error('_capture_image failed: missing BIN_DIR')
        return

    geo_dir = current_app.config.get('GEO_BUILD_DIR')
    if not geo_dir:
        log.error('_capture_image failed: missing GEO_BUILD_DIR')
        return

    with Nginx(bin_dir=bin_dir, geo_dir=geo_dir) as netloc:
        time.sleep(3)

        with Chrome(bin_dir=bin_dir) as chrome:
            local_url = f'http://{netloc}/{http_path}'
            screenshot = chrome.capture_screenshot(local_url)
            log.debug('captured screenshot, stopping chrome...')

        log.debug('stopped chrome, stopping nginx...')

    log.debug('stopped nginx')

    return screenshot


@rq.job
def capture_satellite_image(location_id: int, coordinates: SatelliteCoordinates) -> dict:
    http_path = 'sat?lat={lat}&lng={lng}&zoom={zoom}'.format(
        lat=coordinates.latitude,
        lng=coordinates.longitude,
        zoom=coordinates.zoom,
    )
    log.info(f'{location_id=} {coordinates=}')
    screenshot = _capture_image(http_path)
    if not screenshot:
        return

    image_dir = current_app.config.get('IMAGE_STORE_PATH')
    if not image_dir:
        log.error('capture_satellite_image failed: missing IMAGE_STORE_PATH')
        return

    while (image_path := Path(f'{image_dir}/{secrets.token_hex(18)}.png')).is_file():
        pass

    image_path.write_bytes(screenshot)
    log.info(f'captured satellite screenshot {image_path.name} for {location_id}')


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

    image_dir = current_app.config.get('IMAGE_STORE_PATH')
    if not image_dir:
        log.error('capture_streetview_image failed: missing IMAGE_STORE_PATH')
        return

    while (image_path := Path(f'{image_dir}/{secrets.token_hex(18)}.png')).is_file():
        pass

    image_path.write_bytes(screenshot)

    log.info(f'captured street screenshot {image_path.name} for {location_id}')
