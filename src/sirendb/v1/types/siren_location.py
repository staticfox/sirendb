from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren_location import SirenLocation


class SirenLocationNode(GraphQLType):
    class Meta:
        name = 'SirenLocation'
        sqlalchemy_model = SirenLocation
        sqlalchemy_only_fields = (
            'id',
            'topographic_latitude',
            'topographic_longitude',
            'topographic_zoom',
            'street_latitude',
            'street_longitude',
            'street_heading',
            'street_pitch',
            'street_zoom',
            'installation_timestamp',
            'removal_timestamp',
        )
