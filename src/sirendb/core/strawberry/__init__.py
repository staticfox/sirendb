import strawberry

from .field import (
    SchemaFieldRegistry,
    SchemaFieldBase,
)
from .type_ import SchemaTypeBase


def create_schema():
    return strawberry.Schema(
        query=SchemaFieldRegistry.create_root_type('Query'),
        mutation=SchemaFieldRegistry.create_root_type('Mutation'),
    )
