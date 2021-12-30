from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren_location import SirenLocation


class SirenLocationNode(GraphQLType):
    class Meta:
        name = 'SirenLocation'
        sqlalchemy_model = SirenLocation
        sqlalchemy_only_fields = (
            'id',
            'satellite_latitude',
            'satellite_longitude',
            'satellite_zoom',
            'street_latitude',
            'street_longitude',
            'street_heading',
            'street_pitch',
            'street_zoom',
            'installation_timestamp',
            'removal_timestamp',
            'siren_id',
            'siren',
            'system_id',
            'system',
            'media',
            'created_timestamp',
            'updated_timestamp',
            'created_by',
            'updated_by',
        )
