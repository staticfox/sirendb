from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren_system import SirenSystem


class SirenSystemNode(GraphQLType):
    class Meta:
        name = 'SirenSystem'
        sqlalchemy_model = SirenSystem
        sqlalchemy_only_fields = (
            'created_timestamp',
            'modified_timestamp',
            'name',
            'start_of_service_timestamp',
            'end_of_service_timestamp',
            'in_service',
            'city',
            'county',
            'state',
            'country',
            'postal_code',
            'siren_wiki_url',
            'locations',
        )
