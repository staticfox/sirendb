from typing import Optional

from flask_login import current_user
import strawberry

from sirendb.core.strawberry import GraphQLField

from ..types.user import UserNode


class Query(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(description='Get the viewer')
    def viewer(self) -> Optional[UserNode]:
        if not current_user.is_authenticated:
            return None

        data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'register_timestamp': current_user.register_timestamp,
            'email_verified_timestamp': current_user.email_verified_timestamp,
        }

        return UserNode.ordered_args(data)
