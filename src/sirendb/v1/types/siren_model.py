from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren_model import SirenModel


class SirenModelNode(GraphQLType):
    class Meta:
        name = 'SirenModel'
        sqlalchemy_model = SirenModel
        sqlalchemy_only_fields = (
            'id',
            'created_timestamp',
            'modified_timestamp',
            'name',
            'manufacturer',
            'manufacturer_id',
            'start_of_production',
            'end_of_production',
            'info',
            'revision',
        )
