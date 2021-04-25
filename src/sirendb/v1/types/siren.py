from typing import List

import strawberry

from sirendb.core.strawberry import GraphQLType
from sirendb.core.strawberry.type_ import _resolve_sqlalchemy_result
from sirendb.models.siren import Siren
from sirendb.models.siren_location import SirenLocation
from sirendb.utils.debug import ASSERT

from .siren_location import SirenLocationNode


class SirenNode(GraphQLType):
    class Meta:
        name = 'Siren'
        sqlalchemy_model = Siren
        sqlalchemy_only_fields = (
            'id',
            'active',
            'model',
            'model_id',
        )

    previous_locations: List[SirenLocationNode] = strawberry.field(
        description=(
            'Previous geographic locations where the siren has been installed.'
        )
    )  # type: ignore

    @staticmethod
    def resolve_previous_locations(cls, type_info, row, request_document) -> List[SirenLocationNode]:
        locations = row.locations.order_by(
            SirenLocation.installation_timestamp.desc(),
            SirenLocation.created_timestamp.desc(),
        ).offset(1).all()

        rv = [
            _resolve_sqlalchemy_result(
                cls=cls,
                type_info=type_info,
                row=location,
                request_document=request_document,
            )
            for location in locations
        ]
        for item in rv:
            assert isinstance(item, SirenLocationNode)
        return rv

    current_location: SirenLocationNode = strawberry.field(
        description='Current geographic location of the siren.'
    )  # type: ignore

    @staticmethod
    def resolve_current_location(cls, type_info, row, request_document) -> SirenLocationNode:
        location = row.locations.order_by(
            SirenLocation.installation_timestamp.desc(),
            SirenLocation.created_timestamp.desc(),
        ).first()

        rv = _resolve_sqlalchemy_result(
            cls=cls,
            type_info=type_info,
            row=location,
            request_document=request_document,
        )

        ASSERT(
            (rv is None or isinstance(rv, SirenLocationNode)),
            f'expected SirenLocationNode or None, got {rv}',
        )
        return rv
