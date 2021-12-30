from typing import Optional

from flask_login import current_user
import strawberry

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)
from sirendb.models.siren import Siren
from sirendb.models.siren_model import SirenModel

from ..types.siren import SirenNode


class Input(GraphQLType):
    '''
    Input type of createSiren.
    '''
    __typename__ = 'CreateSirenInput'
    __isinput__ = True

    class Meta:
        node = SirenNode
        only_fields = (
            'active',
            'model_id',
        )


class Output(GraphQLType):
    '''
    Return type of createSiren.
    '''
    __typename__ = 'CreateSirenPayload'

    ok: bool = strawberry.field(
        description='Whether or not the siren was created.'
    )
    message: str = strawberry.field(
        description='Status message related to the creation.'
    )
    siren: Optional[SirenNode] = strawberry.field(
        description='The newely registered siren.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(description='Registers a siren within sirendb.')
    def create_siren(self, form: Input) -> Output:
        if form.model_id and SirenModel.query.get(form.model_id) is None:
            return Output(
                ok=False,
                message='Unknown modelId.',
                siren=None,
            )

        kwargs = {
            k: getattr(form, k)
            for k in form.__annotations__.keys()
        }
        siren = Siren(**kwargs)
        siren.created_by_id = current_user.id
        db.session.add(siren)
        db.session.commit()

        return Output(
            ok=True,
            message='',
            siren=siren,
        )
