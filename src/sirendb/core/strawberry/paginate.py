from __future__ import annotations

from enum import Enum
import functools
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


class PaginatedField:
    def __init__(self, method, node):
        self.method = method
        self.method_name = method.__name__
        self.node = node

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)


def paginated_field(func=None, node=None):
    if func is None:
        return functools.partial(paginated_field, node=node)

    assert node

    return PaginatedField(func, node)


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


class SortingEnum:
    def __init__(self):
        self.enum_to_column = {}
        self.enum = None
        self.strawberry_enum = None

    def add(self, column, direction, enum_value):
        # full_enum_value = enum_value + 'SortEnum'
        self.enum_to_column[enum_value] = {
            'column': column,
            'direction': direction,
            'enum_value': enum_value,
        }

    def make_enum(self, name: str):
        self.enum = Enum(name + 'SortEnum', ' '.join([
            value['enum_value']
            for value in self.enum_to_column.values()
        ]))
        self.strawberry_enum = strawberry.enum(self.enum)

    def get_default(self):
        # TODO: Pick based on primary key
        return self.enum_to_column['ID_ASC']


@strawberry.type
class Paginated(Generic[T]):
    items: List[T]
    count: Optional[int] = None
    page_info: PageInfo = None

    @classmethod
    def paginate(
        cls,
        query: sa.orm.query.Query,
        paginate: Optional[Paginate],
        sort: Optional[str],
        sorter: Optional[SortingEnum],
    ):
        if sort:
            sorting_enum = sorter.enum_to_column.get(sort.name)
        else:
            sorting_enum = sorter.get_default()

        if not paginate:
            paginate = Paginate(
                first=10,
                last=None,
                before=None,
                after=None,
            )

        if paginate.first is not None and paginate.first < 0:
            raise GraphQLError('first may not be less than 0')

        if paginate.last is not None and paginate.last < 0:
            raise GraphQLError('last may not be less than 0')

        if paginate.first and paginate.last:
            raise GraphQLError('first and last may not be specified at the same time.')

        if paginate.before and paginate.after:
            raise GraphQLError('before and after may not be specified at the same time.')

        # query = query.distinct()

        if sorting_enum:
            order_by = getattr(sorting_enum['column'], sorting_enum['direction'])()
            query = query.order_by(order_by)

        if paginate.first is not None:
            query = query.limit(paginate.first)
        else:
            assert paginate.last is not None
            query = query.limit(paginate.last)

        data = query.all()

        return cls(
            items=data,
            count=len(data),
            page_info=PageInfo(
                has_next=False,
                last_cursor='',
            )
        )
