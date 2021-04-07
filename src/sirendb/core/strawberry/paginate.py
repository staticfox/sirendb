from __future__ import annotations
from typing import (
    Generic,
    List,
    TypeVar,
    Optional,
)

import strawberry
from strawberry.field import StrawberryField
import sqlalchemy as sa
from graphql.error.graphql_error import GraphQLError

from .type_ import GraphQLType


@strawberry.type
class PageInfo:
    has_next: bool
    last_cursor: str


class Paginate(GraphQLType):
    __typename__ = 'Paginate'
    __isinput__ = True

    def __bool__(self):
        if self.first is None and self.last is None and self.before is None and self.after is None:
            return False
        return True

    first: Optional[int] = StrawberryField(
        python_name='first',
        graphql_name='first',
        type_=Optional[int],
        description='Return the first number amount of items.',
        default_value=None,
        is_optional=True
    )
    last: Optional[int] = StrawberryField(
        python_name='last',
        graphql_name='last',
        type_=Optional[int],
        description='Return the last number amount of items.',
        default_value=None,
        is_optional=True
    )
    before: Optional[str] = StrawberryField(
        python_name='before',
        graphql_name='before',
        type_=Optional[str],
        description='Return items before the given cursor.',
        default_value=None,
        is_optional=True
    )
    after: Optional[str] = StrawberryField(
        python_name='after',
        graphql_name='after',
        type_=Optional[str],
        description='Return items after the given cursor.',
        default_value=None,
        is_optional=True
    )


T = TypeVar("T")


class GenericSorter(Generic[T]):
    pass


@strawberry.type
class Paginated(Generic[T]):
    items: List[T]
    count: Optional[int] = None
    page_info: PageInfo = None

    @classmethod
    def paginate(cls, query: sa.orm.query.Query, paginate: Paginate):
        # print(f'Paginate\n{paginate=}')
        if not paginate:
            paginate = Paginate(
                first=10,
                last=None,
                before=None,
                after=None,
            )

        first = paginate.first
        last = paginate.last
        before = paginate.before
        after = paginate.after

        if first is not None and first < 0:
            raise GraphQLError('first may not be less than 0')

        if last is not None and last < 0:
            raise GraphQLError('last may not be less than 0')

        if first and last:
            raise GraphQLError('first and last may not be specified at the same time.')

        if before and after:
            raise GraphQLError('before and after may not be specified at the same time.')

        # query = query.distinct()

        # ORDER BY?
        if first is not None:
            query = query.limit(first)  # .order_by(SirenSystem.id.asc())
        else:
            assert last is not None
            query = query.limit(last)  # .order_by(SirenSystem.id.desc())

        data = query.all()

        return cls(
            items=data,
            count=len(data),
            page_info=PageInfo(
                has_next=False,
                last_cursor='',
            )
        )
