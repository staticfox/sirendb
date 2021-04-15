from datetime import datetime
import logging
from typing import Optional

import strawberry

from sirendb.core.db import db
from sirendb.core.rq import rq
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)
from sirendb.jobs.imaging import (
    capture_satellite_image,
    capture_streetview_image,
)
from sirendb.models.siren import Siren
from sirendb.models.siren_location import SirenLocation
from sirendb.models.siren_system import SirenSystem

from ..types.siren_location import SirenLocationNode

log = logging.getLogger('sirendb.v1')


class Input(GraphQLType):
    '''
    Input type of createSirenLocation.
    '''
    __typename__ = 'CreateSirenLocationInput'
    __isinput__ = True

    class Meta:
        node = SirenLocationNode
        only_fields = (
            'satellite_latitude',
            'satellite_longitude',
            'satellite_zoom',
            'street_latitude',
            'street_longitude',
            'street_heading',
            'street_pitch',
            'street_zoom',
            'installation_timestamp',
            'removal_timestamp',
            'siren_id',
            'system_id',
        )


class Output(GraphQLType):
    '''
    Return type of createSirenLocation.
    '''
    __typename__ = 'CreateSirenLocationPayload'

    ok: bool = strawberry.field(
        description='Whether or not the siren location was created.'
    )
    message: str = strawberry.field(
        description='Status message related to the creation.'
    )
    siren_location: Optional[SirenLocationNode] = strawberry.field(
        description='The newely registered siren location.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/graphql',)

    @strawberry.field(description='Registers a siren location within sirendb.')
    def create_siren_location(self, form: Input) -> Output:
        # TODO: validate coordinates are valid

        if not form.siren_id or Siren.query.get(form.siren_id) is None:
            return Output(
                ok=False,
                message='Unknown sirenId.',
                siren_location=None,
            )

        if form.system_id and SirenSystem.query.get(form.system_id) is None:
            return Output(
                ok=False,
                message='Unknown systemId.',
                siren_location=None,
            )

        kwargs = {
            k: getattr(form, k)
            for k in form.__annotations__.keys()
        }
        siren_location = SirenLocation(**kwargs)
        siren_location.created_timestamp = datetime.utcnow()
        db.session.add(siren_location)
        db.session.commit()

        log.debug('/api/v1/graphql mutation createSirenLocation(satellite={satellite}, street={street}, system={system})'.format(  # noqa
            satellite=siren_location.satellite_coordinates is not None,
            street=siren_location.street_coordinates is not None,
            system=siren_location.system_id is not None,
        ))

        queue = rq.get_queue('imaging_for_api')

        if siren_location.satellite_coordinates:
            queue.enqueue(capture_satellite_image, args=(
                siren_location.id,
                siren_location.satellite_coordinates,
            ), job_timeout=300, description='capture satellite coordinates')

        if siren_location.street_coordinates:
            queue.enqueue(capture_streetview_image, args=(
                siren_location.id,
                siren_location.street_coordinates,
            ), job_timeout=300, description='capture streetview coordinates')

        return Output(
            ok=True,
            message='',
            siren_location=siren_location,
        )
