from __future__ import annotations
import typing

import strawberry

from sirendb.core.strawberry import GraphQLField

from ..types.siren import Siren


class Query(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(
        description=(
            'Allows you to search through the list of sirens known to SirenDB.'
        )
    )
    def search_sirens(self) -> typing.List[Siren]:
        '''
        searchSirens description here
        '''
        return [
            Siren(name='...'),
        ]
