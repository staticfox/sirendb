import typing
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import strawberry

from sirendb.core.strawberry import GraphQLType
from sirendb.core.strawberry.paginate import _build_dataclass
from sirendb.models.siren import Siren
from sirendb.models.siren_location import SirenLocation
from sirendb.utils.debug import ASSERT

from .siren_location import SirenLocationNode


class SirenNode(GraphQLType):
    class Meta:
        name = 'Siren'
        sqlalchemy_model = Siren
        sqlalchemy_only_fields = (
            'id',
            'active',
            'model',
            'model_id',
        )

    previous_locations: typing.List[SirenLocationNode] = strawberry.field(
        description=(
            'Previous geographic locations where the siren has been installed.'
        )
    )

    @staticmethod
    def resolve_previous_locations(
        self: SirenLocation,
        gql_ast_document: List[str],
        gql_ast_prefix: str,
        required_keys: List[str],
        late_resolvers: set,
        resolved_cache: dict,
        is_root: bool,
        visited_tables: List[str],
    ) -> typing.List[SirenLocationNode]:
        locations = self.locations.order_by(
            SirenLocation.installation_timestamp.desc(),
            SirenLocation.created_timestamp.desc(),
        ).offset(1).all()

        rv = [
            _build_dataclass(
                type_=SirenLocationNode,
                node=location,
                gql_ast_document=gql_ast_document,
                gql_ast_prefix=gql_ast_prefix,
                late_resolvers=late_resolvers,
                resolved_cache=resolved_cache,
                is_root=is_root,
                required_keys=required_keys,
                visited_tables=visited_tables,
            )
            for location in locations
        ]
        for item in rv:
            assert isinstance(item, SirenLocationNode)
        return rv

    current_location: SirenLocationNode = strawberry.field(
        description='Current geographic location of the siren.'
    )

    @staticmethod
    def resolve_current_location(
        self: SirenLocation,
        gql_ast_document: List[str],
        gql_ast_prefix: str,
        required_keys: List[str],
        late_resolvers: set,
        resolved_cache: dict,
        is_root: bool,
        visited_tables: List[str],
    ) -> SirenLocationNode:
        location = self.locations.order_by(
            SirenLocation.installation_timestamp.desc(),
            SirenLocation.created_timestamp.desc(),
        ).first()

        # breakpoint()
        rv = _build_dataclass(
            type_=SirenLocationNode,
            node=location,
            gql_ast_document=gql_ast_document,
            gql_ast_prefix=gql_ast_prefix,
            late_resolvers=late_resolvers,
            resolved_cache=resolved_cache,
            is_root=is_root,
            required_keys=required_keys,
            visited_tables=visited_tables,
        )

        ASSERT(
            (rv is None or isinstance(rv, SirenLocationNode)),
            f'expected SirenLocationNode or None, got {rv}',
        )
        return rv
