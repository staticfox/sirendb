from datetime import datetime
import re
from typing import Optional

import strawberry
import sqlalchemy as sa
from werkzeug.security import generate_password_hash

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)

from ..types.user import UserNode
from ...models.user import User


class Input(GraphQLType):
    '''
    Input type of registerAccount.
    '''
    __typename__ = 'RegisterAccountInput'
    __isinput__ = True

    username: str = strawberry.field(
        description='The username you would like to be known as.'
    )
    email: str = strawberry.field(
        description='Your E-Mail address used to receive automated notifications.'
    )
    password: str = strawberry.field(
        description='Password used to verify account ownership.'
    )


class Output(GraphQLType):
    '''
    Return type of registerAccount.
    '''
    __typename__ = 'RegisterAccountPayload'

    ok: bool = strawberry.field(
        description='Whether or not the registration was successful.'
    )
    message: str = strawberry.field(
        description='Status message related to the registration.'
    )
    user: Optional[UserNode] = strawberry.field(
        description='The newely registered user.'
    )


class Mutation(GraphQLField):
    @strawberry.field(description='Register for a SirenDB account.')
    def register_account(self, form: Input) -> Output:
        failed_args = {'ok': False, 'user': None}

        username_pattern = re.compile(r'^[a-zA-Z0-9]{3,40}$')
        if not username_pattern.match(form.username):
            return Output(message='invalid username', **failed_args)

        # https://stackoverflow.com/a/21456918
        # Minimum eight characters, at least one uppercase letter,
        # one lowercase letter, one number and one special character:
        password_pattern = re.compile(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )
        if not password_pattern.match(form.password):
            return Output(message='invalid password', **failed_args)

        user = User.query.filter(sa.or_(
            User.username == form.username,
            User.email == form.email,
        )).first()

        if user:
            why = 'email' if user.email == form.email else 'username'
            return Output(message=f'Account with {why} already exists.', **failed_args)

        hashed_pw = generate_password_hash(form.password)

        user = User(
            username=form.username,
            email=form.email,
            password_hash=hashed_pw,
            register_timestamp=datetime.utcnow(),
        )
        db.session.add(user)
        db.session.commit()

        return Output(
            ok=True,
            message='Please verify your email address to log in.',
            user=user,
        )
