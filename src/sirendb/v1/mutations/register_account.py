from typing import Optional

import strawberry

from sirendb.core.strawberry import (
    SchemaFieldBase,
    SchemaTypeBase,
)

from ..types.user import UserNode


@strawberry.input(
    description='Input type of registerAccount.'
)
class RegisterAccountInput:
    username: str = strawberry.field(
        description='The username you would like to be known as.'
    )
    email: str = strawberry.field(
        description='Your E-Mail address used to receive automated notifications.'
    )
    password: str = strawberry.field(
        description='Password used to verify account ownership.'
    )


class RegisterAccountPayload(SchemaTypeBase):
    '''
    Return type of registerAccount.
    '''
    ok: bool = strawberry.field(
        description='Whether or not the registration was successful.'
    )
    message: str = strawberry.field(
        description='Status message related to the registration.'
    )
    user: Optional[UserNode] = strawberry.field(
        description='The newely registered user.'
    )


class Mutation(SchemaFieldBase):
    @strawberry.field(description='Register for a SirenDB account.')
    def register_account(self, form: RegisterAccountInput) -> RegisterAccountPayload:
        return RegisterAccountPayload(
            ok=False,
            message='registration disabled',
            user=None,
        )
