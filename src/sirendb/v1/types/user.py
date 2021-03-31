import strawberry

from sirendb.core.strawberry import SchemaTypeBase
from sirendb.models.user import User


class UserNode(SchemaTypeBase):
    class Meta:
        name = 'User'
        sqlalchemy_model = User
        sqlalchemy_only_fields = (
            'email',
            'email_verified_timestamp',
            'register_timestamp',
            'username',
        )
