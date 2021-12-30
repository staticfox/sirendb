from enum import Enum
import functools
import re
from typing import (
    Any,
    Generic,
    List,
    Optional,
    TypeVar,
)

from graphql.error.graphql_error import GraphQLError
import strawberry
from strawberry.ast import ast_from_info
from strawberry.field import StrawberryField
from strawberry.types.info import Info
import sqlalchemy as sa

from .scalars import LimitedStringScalar
from .type_ import GraphQLType


class PaginatedField:
    def __init__(self, method, node):
        self.method = method
        self.method_name = method.__name__
        self.node = node


def paginated_field(func=None, node=None):
    if func is None:
        return functools.partial(paginated_field, node=node)

    assert node

    return PaginatedField(func, node)


@strawberry.type
class PageInfo:
    has_next: bool
    last_cursor: Optional[str]


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


def wildcard_to_sql(value: str):
    # TODO: tests tests tests
    new_str = ''

    for index, char in enumerate(value):
        if index + 1 < len(value):
            next_char = value[index + 1]
        else:
            next_char = None

        if char == '*':
            if next_char in ('*', '?'):
                raise GraphQLError('invalid search expression')
            new_str += '%'
            continue

        if char == '?' and next_char == '?':
            raise GraphQLError('invalid search expression')

        if re.compile(r'[^a-zA-Z0-9\%\*]').search(value):
            raise GraphQLError('invalid search expression')
        elif not re.compile(r'[a-zA-Z0-9]').search(value):
            raise GraphQLError('invalid search expression')

        new_str += char

    return new_str


def get_column_by_key(query, name: str):
    for column in query._raw_columns[0].columns:
        if column.key == name:
            return column
    assert False


class SearchType:
    def __init__(self):
        self.invalid_message = None
        self.match_any = None
        self.match_one = False

    @classmethod
    def filter_by(self, query, name: str, value: Any, type_: type):
        if type_ in (LimitedStringScalar, str):
            expression = wildcard_to_sql(value)
            if '%' in expression or '?' in expression:
                column = get_column_by_key(query, name)
                return query.filter(column.ilike(value))
            else:
                return query.filter_by(**{name: value})
            assert False
        elif isinstance(type_, bool):
            column = get_column_by_key(query, name)
            return query.filter(column.is_(value))
        else:
            return query.filter_by(**{name: value})
        assert False


@strawberry.type
class Paginated(Generic[T]):
    items: List[T]
    count: Optional[int] = None
    total_count: Optional[int] = None
    page_info: PageInfo = None

    @classmethod
    def paginate(
        cls,
        query: sa.orm.query.Query,
        _node,  # TODO type
        paginate: Optional[Paginate],
        filter_,  # TODO type
        filter_type,  # TODO type
        sort: Optional[str],
        sorter: Optional[SortingEnum],
        info: Info,
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

        if filter_:
            for field_name, field_type in filter_.__annotations__.items():
                field_value = filter_.__dict__[field_name]
                if field_value is not None:
                    query = SearchType.filter_by(query, field_name, field_value, field_type)

        if sorting_enum:
            order_by = getattr(sorting_enum['column'], sorting_enum['direction'])()
            query = query.order_by(order_by)

        total = query.count()

        if paginate.first is not None:
            query = query.limit(paginate.first)
        else:
            assert paginate.last is not None
            query = query.limit(paginate.last)

        ast = ast_from_info(info)
        request_document = ast.document_python_names[0][1]
        request_document = request_document[request_document.index('items') + 1]
        data = _node.from_sqlalchemy_model(query.all(), info, request_document)

        if data:
            last_data = data[-1]
            last_cursor = last_data.id
        else:
            last_cursor = None

        return cls(
            items=data,
            count=len(data),
            total_count=total,
            page_info=PageInfo(
                has_next=len(data) > 0 and total > len(data),
                last_cursor=last_cursor,
            )
        )
