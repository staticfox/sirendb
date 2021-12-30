import secrets
from typing import Optional

from sirendb.core.redis import redis

from .results import SaveResult


class StorageBase:
    def __init__(self, config):
        self.base_url = config.get('base_url')
        self.enabled = True

    def generate_key(self) -> str:
        while True:
            key = secrets.token_hex(16)

            if redis.sadd('media_ids', key):
                return key

    def save(self, data: bytes, file_extension: str, mime_type: str) -> Optional[SaveResult]:
        pass

    def get(self, key: str) -> Optional[bytes]:
        pass

    def delete(self, key: str) -> bool:
        pass
