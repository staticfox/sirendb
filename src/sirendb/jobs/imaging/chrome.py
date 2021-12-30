import base64
import logging
import sys
import time
from typing import Optional

from flask import current_app
from selenium.webdriver import (
    Chrome as ChromeDriver,
    ChromeOptions,
)

log = logging.getLogger('sirendb.imaging.chrome')


class Chrome:
    def __init__(self, bin_dir: str):
        self._bin_dir = bin_dir
        self._driver = None

    def capture_screenshot(self, url: str) -> Optional[bytes]:
        if not self._driver:  # pragma: nocover
            return None

        self._driver.get(url)

        # FIXME Wait til it's loaded
        if not current_app.testing or current_app.config.get('USE_REAL_NGINX'):
            time.sleep(3)

        log.debug('taking screenshot...')
        response = self._driver.execute_cdp_cmd('Page.captureScreenshot', {})

        return base64.b64decode(response['data'])

    def __enter__(self):
        options = ChromeOptions()
        options.add_argument('disable-gpu')
        options.add_argument('disable-dev-shm-usage')
        options.add_argument('headless')
        options.add_argument('window-size=1080,1080')
        options.binary_location = f'{self._bin_dir}/latest/chrome'

        self._driver = ChromeDriver(
            options=options,
            executable_path=f'{self._bin_dir}/chromedriver',
        )

        return self

    def __exit__(self, *args, **kwargs):
        # dump console log to stdout, will be shown when test fails
        for entry in self._driver.get_log('browser'):
            sys.stderr.write('[browser console] ')
            sys.stderr.write(repr(entry))
            sys.stderr.write("\n")

        # Teardown Selenium.
        try:
            self._driver.quit()
        except Exception:
            pass
