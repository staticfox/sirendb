from typing import (
    Any,
    Optional,
)

from sirendb.core.strawberry import GraphQLField
from sirendb.core.strawberry.field import SortingEnum
from sirendb.core.strawberry.paginate import Paginate, paginated_field
from sirendb.models.siren_location import SirenLocation

from ..types.siren_location import SirenLocationNode


# TODO: Don't expose this maybe?
class Query(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @paginated_field(node=SirenLocationNode)
    def siren_locations(
        self,
        # Custom search
        # geolocation: Optional[Tuple[float, float]],

        # Provided by paginated_field
        paginate: Optional[Paginate] = None,
        sort: Optional[SortingEnum] = None,
        filter: Optional[Any] = None,
    ):
        '''
        Return siren locations.
        '''
        return SirenLocation.query
