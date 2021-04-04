import strawberry

from .field import (
    GraphQLField,
    SchemaFieldRegistry,
)
from .type_ import GraphQLType


def create_schema():
    return strawberry.Schema(
        query=SchemaFieldRegistry.create_root_type('Query'),
        mutation=SchemaFieldRegistry.create_root_type('Mutation'),
    )
