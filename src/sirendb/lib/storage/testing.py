from pathlib import Path
from typing import Optional

from .base import StorageBase
from .results import SaveResult


class TestingBackend(StorageBase):
    def save(self, data: bytes, file_extension: str, mime_type: str) -> Optional[SaveResult]:
        filesystem_key = self.generate_key()
        filename = f'{filesystem_key}.{file_extension}'

        image_path = Path('/images/' + filename)
        filesystem_uri = 'testing://' + str(image_path)

        return SaveResult(
            filesystem_key=filesystem_key,
            filesystem_uri=filesystem_uri,
        )
