import typing

import strawberry

from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren import Siren
from sirendb.models.siren_location import SirenLocation

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

    previous_locations: typing.List[SirenLocationNode] = strawberry.field(
        description=(
            'Previous geographic locations where the siren has been installed.'
        )
    )

    @staticmethod
    def resolve_previous_locations(self: SirenLocation) -> typing.List[SirenLocation]:
        return self.locations.order_by(
            SirenLocation.installation_timestamp.desc(),
            SirenLocation.created_timestamp.desc(),
        ).offset(1).all()

    current_location: SirenLocationNode = strawberry.field(
        description='Current geographic location of the siren.'
    )

    @staticmethod
    def resolve_current_location(self: SirenLocation) -> SirenLocation:
        return self.locations.order_by(
            SirenLocation.installation_timestamp.desc(),
            SirenLocation.created_timestamp.desc(),
        ).first()
