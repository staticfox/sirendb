from pathlib import Path
from typing import Optional

from .base import StorageBase
from .results import SaveResult


class FilesystemBackend(StorageBase):
    def __init__(self, config: dict):
        self._path = config.get('path', '')
        super().__init__(config)

    def save(self, data: bytes, file_extension: str, mime_type: str) -> Optional[SaveResult]:
        filesystem_key = self.generate_key()
        filename = f'{filesystem_key}.{file_extension}'

        image_path = Path(self._path + '/' + filename)
        image_path.write_bytes(data)
        filesystem_uri = 'filesystem://' + str(image_path)

        return SaveResult(
            filesystem_key=filesystem_key,
            filesystem_uri=filesystem_uri,
        )
