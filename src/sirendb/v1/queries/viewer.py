from __future__ import annotations

import strawberry

from sirendb.core.strawberry import GraphQLField

from ..types.user import UserNode


class Query(GraphQLField):
    @strawberry.field(description='Get the viewer')
    def viewer(self) -> UserNode:
        return UserNode(
            id=1,
            username='test',
            email='test',
        )
