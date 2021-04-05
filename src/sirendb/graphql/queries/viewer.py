from __future__ import annotations
from typing import Optional

from flask_login import current_user
import strawberry

from sirendb.core.strawberry import GraphQLField

from ..types.user import UserNode


class Query(GraphQLField):
    @strawberry.field(description='Get the viewer')
    def viewer(self) -> Optional[UserNode]:
        if not current_user.is_authenticated:
            return None

        return UserNode(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            register_timestamp=current_user.register_timestamp,
            email_verified_timestamp=current_user.email_verified_timestamp,
        )
