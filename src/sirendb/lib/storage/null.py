from .base import StorageBase


class NullBackend(StorageBase):
    def __init__(self, config):
        super().__init__(config)
        self.enabled = False

    def generate_key(self) -> str:
        return ''
