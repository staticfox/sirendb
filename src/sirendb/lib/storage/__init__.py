from sirendb.utils.lang import DelayedInstance

from .filesystem import FilesystemBackend
from .null import NullBackend
from .testing import TestingBackend


class Storage(DelayedInstance):
    def init_app(self, app):
        config = app.config.get_namespace('IMAGE_STORE_')

        backends = {
            'fs': FilesystemBackend,
            'test': TestingBackend,
        }

        backend_type = config.get('type', '').lower()
        backend = backends.get(backend_type, NullBackend)

        self.set_instance(backend(config))


storage = Storage()
