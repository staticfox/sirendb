import pytest

from sirendb.jobs.imaging import (
    chrome,
    nginx,
)
from sirendb.jobs.imaging.nginx import Nginx
from tests.utils.networking import (
    Popen,
    Socket,
)

from .chrome_driver import FakeChromeDriver


# class Popen(_Popen):
#     _want_delay = False


@pytest.fixture(autouse=True)
def patch_subprocess(app, monkeypatch):
    if app.config.get('USE_REAL_NGINX'):
        yield
        return

    monkeypatch.setattr(nginx, 'Popen', Popen)
    monkeypatch.setattr(nginx, 'Socket', Socket)

    yield


@pytest.fixture(autouse=True)
def patch_chrome_driver(app, monkeypatch):
    if app.config.get('USE_REAL_CHROME'):
        yield
        return

    def add_call(*args, **kwargs):
        with FakeChromeDriver(*args, **kwargs) as driver:
            return driver

    monkeypatch.setattr(chrome, 'ChromeDriver', add_call)

    yield


@pytest.fixture(autouse=True)
def patch_open(app, monkeypatch):
    if app.config.get('USE_REAL_NGINX'):
        yield
        return

    monkeypatch.setattr(Nginx, '_write_config', lambda self: '')
    monkeypatch.setattr(Nginx, '_remove_config', lambda self: '')

    yield
