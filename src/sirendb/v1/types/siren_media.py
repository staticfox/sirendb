from typing import (
    List,
    Optional,
)

import strawberry

from sirendb.core.strawberry import GraphQLType
from sirendb.models.siren_media import SirenMedia
from sirendb.lib.storage import storage


class SirenMediaNode(GraphQLType):
    class Meta:
        name = 'SirenMedia'
        sqlalchemy_model = SirenMedia
        sqlalchemy_only_fields = (
            'id',
            'media_type',
            'mimetype',
            'kilobytes',
            'location_id',
            'location',
        )

    download_url: Optional[str] = strawberry.field(
        description='Network location of this media.',
    )

    @staticmethod
    def resolve_download_url(
        self: SirenMedia,
        gql_ast_document: List[str],
        gql_ast_prefix: str,
        required_keys: List[str],
        late_resolvers: set,
        resolved_cache: dict,
        is_root: bool,
        visited_tables: List[str],
    ) -> Optional[str]:
        if not storage.enabled:
            return None
        return storage.base_url + '/' + self.filename
