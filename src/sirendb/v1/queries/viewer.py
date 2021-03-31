from __future__ import annotations

import strawberry

from sirendb.core.strawberry import SchemaFieldBase

from ..types.user import UserNode


class Query(SchemaFieldBase):
    @strawberry.field(description='Get the viewer')
    def viewer(self) -> UserNode:
        return UserNode(
            id=1,
            username='test',
            email='test',
        )
