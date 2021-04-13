from datetime import datetime
from typing import Optional

import strawberry

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)
from sirendb.models.siren_model import SirenModel
from sirendb.models.siren_manufacturer import SirenManufacturer

from ..types.siren_model import SirenModelNode


class Input(GraphQLType):
    '''
    Input type of createSirenModel.
    '''
    __typename__ = 'CreateSirenModelInput'
    __isinput__ = True

    class Meta:
        node = SirenModelNode
        only_fields = (
            'name',
            'manufacturer_id',
            'start_of_production',
            'end_of_production',
            'info',
            'revision',
        )


class Output(GraphQLType):
    '''
    Return type of createSirenModel.
    '''
    __typename__ = 'CreateSirenModelPayload'

    ok: bool = strawberry.field(
        description='Whether or not the siren model was created.'
    )
    message: str = strawberry.field(
        description='Status message related to the creation.'
    )
    siren_model: Optional[SirenModelNode] = strawberry.field(
        description='The newely registered siren model.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(description='Registers a siren model within sirendb.')
    def create_siren_model(self, form: Input) -> Output:
        if form.manufacturer_id and SirenManufacturer.query.get(form.manufacturer_id) is None:
            return Output(
                ok=False,
                message='Unknown manufacturerId.',
                siren_model=None,
            )

        kwargs = {
            k: getattr(form, k)
            for k in form.__annotations__.keys()
        }
        siren_model = SirenModel(**kwargs)
        siren_model.created_timestamp = datetime.utcnow()
        db.session.add(siren_model)
        db.session.commit()

        return Output(
            ok=True,
            message='',
            siren_model=siren_model,
        )
