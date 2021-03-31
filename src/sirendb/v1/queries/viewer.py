from __future__ import annotations

import strawberry

from sirendb.core.strawberry import (
    SchemaFieldBase,
    SchemaTypeBase,
)
from sirendb.models.user import User


class UserNode(SchemaTypeBase):
    class Meta:
        name = 'User'
        sqlalchemy_model = User

    name: str = strawberry.field(
        description='The name of the siren'
    )


class Query(SchemaFieldBase):
    @strawberry.field(description='Get the viewer')
    def viewer(self) -> UserNode:
        return UserNode(
            id=1,
            username='test',
            email='test',
        )
