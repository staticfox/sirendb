from typing import (
    Any,
    Optional,
)

from strawberry.types.info import Info

from sirendb.core.strawberry import GraphQLField
from sirendb.core.strawberry.field import SortingEnum
from sirendb.core.strawberry.paginate import Paginate, paginated_field
from sirendb.models.siren_model import SirenModel

from ..types.siren_model import SirenModelNode


class Query(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @paginated_field(node=SirenModelNode)
    def siren_models(
        self,
        # Custom search
        # geolocation: Optional[Tuple[float, float]],

        # Provided by paginated_field
        info: Info,
        paginate: Optional[Paginate] = None,
        sort: Optional[SortingEnum] = None,
        filter: Optional[Any] = None,
    ):
        '''
        Return siren models.
        '''
        return SirenModel.query
