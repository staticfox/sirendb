from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren import Siren


class SirenNode(GraphQLType):
    class Meta:
        name = 'Siren'
        sqlalchemy_model = Siren
        sqlalchemy_only_fields = (
            'id',
            'active',
            'model',
            'locations',
        )
