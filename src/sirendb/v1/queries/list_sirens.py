from __future__ import annotations
import typing

import strawberry

from sirendb.core.strawberry import SchemaFieldBase


@strawberry.type(
    name='Siren',
    description=(
        'Describes the attributes of an outdoor warning siren.'
    )
)
class Siren:
    '''
    Siren description here
    '''
    name: str = strawberry.field(
        description='The name of the siren'
    )


class Query(SchemaFieldBase):
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
