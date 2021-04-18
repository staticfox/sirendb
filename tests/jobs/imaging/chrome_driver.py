from __future__ import annotations

import base64
from typing import (
    Any,
    Dict,
    List,
)


class FakeChromeDriver:
    def __init__(self, *args, **kwargs):
        pass

    def execute_cdp_cmd(self, cmd_name: str, options: dict) -> dict:
        return {
            'data': base64.b64encode(b'data'),
        }

    def get(self, url: str) -> None:
        pass

    def get_log(self, log_name: str) -> List[Dict[str, Any]]:
        return []

    def quit(self) -> None:
        pass

    def __enter__(self, *args, **kwargs) -> FakeChromeDriver:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        pass
