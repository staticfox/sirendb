from __future__ import annotations
from typing import Optional

from sirendb.core.strawberry import GraphQLField
from sirendb.core.strawberry.field import paginated_field
from sirendb.core.strawberry.paginate import Paginate
from sirendb.models.siren_system import SirenSystem

from ..types.siren_system import SirenSystemNode


class Query(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @paginated_field(node=SirenSystemNode)
    def siren_systems(self, paginate: Optional[Paginate] = None):
        '''
        Return siren systems.
        '''
        return SirenSystem.query
