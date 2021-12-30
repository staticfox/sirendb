from flask_login import login_user
import strawberry
from werkzeug.security import check_password_hash

from sirendb.models.user import User
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)


class Input(GraphQLType):
    '''
    Input type of login.
    '''
    __typename__ = 'LoginInput'
    __isinput__ = True

    email: str = strawberry.field(
        description='Your accounts email address.'
    )
    password: str = strawberry.field(
        description='Password used to verify account ownership.'
    )


class Output(GraphQLType):
    '''
    Return type of login.
    '''
    __typename__ = 'LoginPayload'

    ok: bool = strawberry.field(
        description='Whether or not your login request was processed successfully.'
    )
    message: str = strawberry.field(
        description='Status message related to logging in.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/auth-graphql',)

    @strawberry.field(description='Log in to sirendb.')
    def login(self, form: Input) -> Output:
        user = User.query.filter_by(email=form.email).one_or_none()
        if not user:
            return Output(
                ok=False,
                message='Email not found.',
            )

        if not check_password_hash(user.password_hash, form.password):
            return Output(
                ok=False,
                message='Invalid password.',
            )

        login_user(user)

        # return redirect('http://10.120.70.4:3000/')
        return Output(
            ok=True,
            message='',
        )
