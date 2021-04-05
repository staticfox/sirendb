import strawberry

from sirendb.core.strawberry import GraphQLType
from sirendb.models.user import User


class UserNode(GraphQLType):
    class Meta:
        name = 'User'
        sqlalchemy_model = User
        sqlalchemy_only_fields = (
            'id',
            'username',
            'email',
            'register_timestamp',
            'email_verified_timestamp',
        )
