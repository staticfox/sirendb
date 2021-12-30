from enum import (
    auto,
    Enum,
)


class SirenType(Enum):
    INVALID = auto()
    MECHANICAL = auto()
    ELECTRO_MECHANICAL = auto()
    ELETRONIC = auto()

    # never re-order, always add to the end.
