from flask_login import logout_user
import strawberry

from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)


class Output(GraphQLType):
    '''
    Return type of logout.
    '''
    __typename__ = 'LogoutPayload'

    ok: bool = strawberry.field(
        description='Whether or not your logout request was processed successfully.'
    )
    message: str = strawberry.field(
        description='Status message related to logging out.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/auth-graphql',)

    @strawberry.field(description='Log out of sirendb.')
    def logout(self) -> Output:
        logout_user()

        return Output(
            ok=True,
            message='',
        )
