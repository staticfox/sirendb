from flask_login import current_user
import strawberry

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)
from sirendb.models.siren_manufacturer import SirenManufacturer

from ..types.siren_manufacturer import SirenManufacturerNode


class Input(GraphQLType):
    '''
    Input type of createSirenManufacturer.
    '''
    __typename__ = 'CreateSirenManufacturerInput'
    __isinput__ = True

    class Meta:
        node = SirenManufacturerNode
        only_fields = (
            'name',
            'founded_timestamp',
            'defunct_timestamp',
            'info',
        )


class Output(GraphQLType):
    '''
    Return type of createSirenManufacturer.
    '''
    __typename__ = 'CreateSirenManufacturerPayload'

    ok: bool = strawberry.field(
        description='Whether or not the siren manufacturer was created.'
    )
    message: str = strawberry.field(
        description='Status message related to the creation.'
    )
    siren_manufacturer: SirenManufacturerNode = strawberry.field(
        description='The newely registered siren manufacturer.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(description='Registers a siren manufacturer within sirendb.')
    def create_siren_manufacturer(self, form: Input) -> Output:
        kwargs = {
            k: getattr(form, k)
            for k in form.__annotations__.keys()
        }
        siren_manufacturer = SirenManufacturer(**kwargs)
        siren_manufacturer.created_by_id = current_user.id
        db.session.add(siren_manufacturer)
        db.session.commit()

        return Output(
            ok=True,
            message='',
            siren_manufacturer=siren_manufacturer,
        )
