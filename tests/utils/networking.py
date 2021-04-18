from __future__ import annotations

from socket import (
    AddressFamily,
    SocketKind,
)
from typing import Tuple


class Socket:
    _times_instanced = 0

    def __init__(self, address_family: AddressFamily, socket_kind: SocketKind):
        self._address_family = address_family
        self._socket_kind = socket_kind

    def connect_ex(self, addr: Tuple[str, int]):
        self.__class__._times_instanced += 1

        if self.__class__._times_instanced > 3:
            self.__class__._times_instanced = 0
            return 0

        return 111

    def __enter__(self) -> Socket:
        return self

    def __exit__(self, *args, **kwargs):
        pass


class Popen:
    _want_delay = False
    _times_instanced = 0

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._first_poll_call = 0
        self.__class__._times_instanced += 1

    def terminate(self):
        pass

    def kill(self):
        pass

    def poll(self) -> bool:
        if not self.__class__._want_delay:
            return False

        if self.__class__._times_instanced == 2:
            return True
        return False
