from datetime import datetime

import strawberry

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)
from sirendb.models.siren_system import SirenSystem

from ..types.siren_system import SirenSystemNode


class Input(GraphQLType):
    '''
    Input type of createSirenSystem.
    '''
    __typename__ = 'CreateSirenSystemInput'
    __isinput__ = True

    class Meta:
        node = SirenSystemNode
        only_fields = (
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
        )


class Output(GraphQLType):
    '''
    Return type of createSirenSystem.
    '''
    __typename__ = 'CreateSirenSystemPayload'

    ok: bool = strawberry.field(
        description='Whether or not the siren system was created.'
    )
    message: str = strawberry.field(
        description='Status message related to the creation.'
    )
    siren_system: SirenSystemNode = strawberry.field(
        description='The newely registered siren system.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(description='Registers a siren system within sirendb.')
    def create_siren_system(self, form: Input) -> Output:
        kwargs = {
            k: getattr(form, k)
            for k in form.__annotations__.keys()
        }
        siren_system = SirenSystem(**kwargs)
        siren_system.created_timestamp = datetime.utcnow()
        db.session.add(siren_system)
        db.session.commit()

        return Output(
            ok=True,
            message='',
            siren_system=siren_system,
        )
