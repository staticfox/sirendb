from pathlib import Path
import secrets
from typing import (
    NamedTuple,
    Optional,
)

from sirendb.core.redis import redis


class UploadResult(NamedTuple):
    filesystem_key: str
    filesystem_uri: str


class StorageBase:
    def __init__(self, config):
        self.base_url = config.get('base_url')
        self.enabled = True

    def generate_key(self) -> Optional[str]:
        while True:
            key = secrets.token_hex(16)

            if redis.sadd('media_ids', key):
                return key

    def upload(self, data: bytes, file_extension: str, mime_type: str) -> Optional[UploadResult]:
        pass

    def download(self, key: str) -> Optional[bytes]:
        pass

    def delete(self, key: str) -> bool:
        pass


class NullBackend(StorageBase):
    def __init__(self, config):
        super().__init__(config)
        self.enabled = False

    def generate_key(self) -> Optional[str]:
        return None


class Filesystem(StorageBase):
    def __init__(self, config: dict):
        self._path = config.get('path')
        super().__init__(config)

    def upload(self, data: bytes, file_extension: str, mime_type: str) -> Optional[UploadResult]:
        filesystem_key = self.generate_key()
        filename = f'{filesystem_key}.{file_extension}'

        image_path = Path(self._path + '/' + filename)
        image_path.write_bytes(data)
        filesystem_uri = 'filesystem://' + str(image_path)

        return UploadResult(
            filesystem_key=filesystem_key,
            filesystem_uri=filesystem_uri,
        )


class TestingBackend(StorageBase):
    def upload(self, data: bytes, file_extension: str, mime_type: str) -> Optional[UploadResult]:
        filesystem_key = self.generate_key()
        filename = f'{filesystem_key}.{file_extension}'

        image_path = Path('/images/' + filename)
        filesystem_uri = 'testing://' + str(image_path)

        return UploadResult(
            filesystem_key=filesystem_key,
            filesystem_uri=filesystem_uri,
        )


class Storage:
    def __init__(self):
        self.__local = None

    def init_app(self, app):
        config = app.config.get_namespace('IMAGE_STORE_')
        if not config:
            self.__local = NullBackend({})
            return

        backends = {
            'fs': Filesystem,
            'test': TestingBackend,
        }

        backend_type = config.get('type', '').lower()
        backend = backends.get(backend_type, NullBackend)

        self.__local = backend(config)

    def __getattr__(self, name):
        if name in ('__init__', 'init_app'):
            return self.__dict__[name]
        elif name == '__local':
            return self.__local
        else:
            return getattr(self.__local, name)


storage = Storage()
