from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren_manufacturer import SirenManufacturer


class SirenManufacturerNode(GraphQLType):
    class Meta:
        name = 'SirenManufacturer'
        sqlalchemy_model = SirenManufacturer
        sqlalchemy_only_fields = (
            'id',
            'name',
            'founded_timestamp',
            'defunct_timestamp',
            'info',
        )
