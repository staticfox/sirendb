from __future__ import annotations

from collections import OrderedDict
import inspect
from typing import (
    Any,
    Dict,
    Iterator,
    Optional,
    Type,
)

import strawberry
from strawberry.field import StrawberryField
import sqlalchemy as sa

from .paginate import (
    Paginate,
    Paginated,
    PaginatedField,
    SortingEnum,
)
from .scalars import (
    LimitedStringScalar,
    StringLimitExceeded,
)


@strawberry.type
class NullField:
    ok: bool = strawberry.field(
        description='This will be irrelevant at some point.'
    )


@strawberry.field(description='TODO')
def null_query(self) -> NullField:
    strawberry.field(description='TODO')
    return NullField(ok=True)


def decl_enum(node: GraphQLField) -> SortingEnum:
    sorter = SortingEnum()

    for column in node.Meta.sqlalchemy_model.__table__.columns:
        if isinstance(column, sa.sql.schema.Column):
            key = column.key.upper()

            for direction in ('_ASC', '_DESC'):
                enum_value = key + direction
                sorter.add(column=column, direction=direction[1:].lower(), enum_value=enum_value)

    sorter.make_enum(node.Meta.name)
    return sorter


def make_filters(node: GraphQLField) -> Dict[str, StrawberryField]:
    filters = {}

    sqlalchemy_only_fields = getattr(node.Meta, 'sqlalchemy_only_fields', [])

    for column in node.Meta.sqlalchemy_model.__table__.columns:
        if isinstance(column, sa.sql.schema.Column):
            if sqlalchemy_only_fields and column.key not in sqlalchemy_only_fields:
                continue

            if column.type.python_type not in (str, LimitedStringScalar, bool, int):
                continue

            type_ = column.type.python_type
            description = column.doc
            if description is not None:
                description = description.strip().rstrip()

            # Allow the type itself to raise the GraphQL error
            # instead of doing basic repetitive string size checks
            # in every single resolver.
            if column.type.python_type is str and column.type.length:
                type_ = LimitedStringScalar
                max_length = column.type.length

                # So people are aware when they read the docs.
                if description is None:
                    description = ''
                description += f' String size may not exceed {max_length} characters.'

                def parse_value(value, _max_length=max_length):
                    if len(value) > _max_length:
                        raise StringLimitExceeded
                    return value

            filters[column.key] = StrawberryField(**{
                'python_name': column.key,
                'graphql_name': column.key,
                'type_': type_,
                'is_optional': column.nullable,
                'default_value': column.default,
                'description': description,
            })

    return filters


def make_filter(node: GraphQLField):
    fields = make_filters(node)
    cls_namespce = {
        '__annotations__': {},
    }

    for field_name, field_value in fields.items():
        cls_namespce['__annotations__'][field_name] = field_value.type
        cls_namespce[field_name] = field_value

    name = node.Meta.name + 'Filter'

    # Setup our Strawberry type so dataclass is happy.
    cls = type.__new__(type, name, (object,), cls_namespce)
    straberry_cls = strawberry.input(
        cls,
        name=name,
        description=f'Filters the collection of {node.Meta.name} objects.',
    )

    # Now that everything has been created properly, we can
    # re-order the type definition so fields will be sent
    # to GraphQL in alphabetical order.
    straberry_cls._type_definition._fields = sorted(
        straberry_cls._type_definition._fields,
        key=lambda field: field.graphql_name
    )
    return straberry_cls


class SchemaFieldRegistry(type):
    def __new__(meta: 'SchemaFieldRegistry', name: str, bases: tuple, namespace: Dict[str, Any]):
        if not hasattr(meta, 'registry'):
            meta.registry = {}

        if not hasattr(meta, 'endpoints'):
            meta.endpoints = set()

        if not bases:
            return type.__new__(meta, name, bases, namespace)

        if name not in ('Query', 'Mutation'):
            raise RuntimeError(
                'You subclassed GraphQLField but your class\'s name is neither\n'
                'Query nor Mutation. Rename your class or remove GraphQLField.'
            )

        if not namespace.get('__endpoints__'):
            raise RuntimeError(
                'You subclassed GraphQLField but your class\'s does not specify\n'
                'the endpoints it should be exposed to.\n'
                'Make sure you add __endpoints__.'
            )

        for key, value in namespace.items():
            if key.startswith('_'):
                continue

            # Convert this to a regular GraphQL field
            if isinstance(value, PaginatedField):
                sig = inspect.signature(value.method)

                # Generate an enum for order_by
                sorting_enum = decl_enum(value.node)

                # Generate search fields
                filter_type = make_filter(value.node)

                # Since Strawberry does not have any support for relays,
                # we have to implement pagination ourselves. To make things
                # simple to implement, we override the resolver's annotations
                # as well as the resolver itself to implement pagination with
                # dynamically created sorters via enums.
                def paginated_request(*args, **kwargs):
                    query = value.method(*args, **kwargs)
                    if 'filter' in kwargs:
                        kwargs['filter_'] = kwargs['filter']
                        del kwargs['filter']
                    return Paginated.paginate(query, sorter=sorting_enum, filter_type=filter_type, **kwargs)

                # Make the wrapper impersonate the actual resolver
                paginated_request.__name__ = value.method_name
                paginated_request.__annotations__ = {
                    'paginate': Optional[Paginate],
                    'filter': Optional[filter_type],
                    'sort': Optional[sorting_enum.strawberry_enum],
                    'return': Paginated[value.node],
                }
                paginated_request.__signature__ = sig
                # HACKHACK: Strawberry will try to resolve the paginated type's
                #           python node. Since it's not defined within this scope,
                #           we have to export it to prevent a NameError.
                locals()[value.node.__name__] = value.node
                description = value.method.__doc__
                if description is not None:
                    description = description.strip().rstrip()
                namespace[value.method_name] = strawberry.field(
                    paginated_request, description=description
                )

        cls = type.__new__(meta, name, bases, namespace)
        meta.registry.setdefault(name, {})

        for endpoint in cls.__endpoints__:
            meta.endpoints.add(endpoint)
            meta.registry[name].setdefault(endpoint, set())
            meta.registry[name][endpoint].add(cls)
            meta.registry[name][endpoint] -= set(bases)

        return cls

    @classmethod
    def create_root_type(meta: 'SchemaFieldRegistry', type_name: str, endpoint: str) -> Optional[Type]:
        namespace = {}
        namespace_class_map = {}
        for Class in meta.registry.get(type_name, {}).get(endpoint, []):
            for attr_name, attr_value in Class.__dict__.items():
                # FIXME: One glaring issue with this approach is that now resolvers may not
                #        call member functions.
                # print(f'{Class.__name__}.{attr_name} {attr_value=}')
                if attr_name.startswith('_') or not isinstance(attr_value, StrawberryField):
                    continue
                if attr_name in namespace:
                    raise RuntimeError(
                        f'You tried to specify {Class.__module__}.{type_name}.{attr_name}\n'
                        f'but it is already defined in {namespace_class_map[attr_name].__module__}.{type_name}.\n'
                        'Remove or rename one of the entries.'
                    )
                namespace[attr_name] = attr_value
                namespace_class_map[attr_name] = Class

        # Endpoint did not contain this type or vice versa
        if not namespace:
            return None

        # Alphabetically sort fields so they're easy to find
        # within the documentation.
        namespace = OrderedDict(sorted(namespace.items()))
        cls = type.__new__(type, type_name, (object,), namespace)
        return strawberry.type(cls, description=(
            f'The root {type_name} object for interacting with SirenDB\'s GraphQL API.'
        ))

    @classmethod
    def schema_for_endpoint(meta: 'SchemaFieldRegistry') -> Iterator[Type]:
        for endpoint in meta.endpoints:
            schema_kwargs = {}

            Query = meta.create_root_type('Query', endpoint)
            if Query:
                schema_kwargs['query'] = Query
            else:
                cls = type.__new__(type, 'Query', (object,), {
                    '__endpoints__': (endpoint,),
                    'null_query': null_query,
                })
                schema_kwargs['query'] = strawberry.type(cls, name='Query')

            Mutation = meta.create_root_type('Mutation', endpoint)
            if Mutation:
                schema_kwargs['mutation'] = Mutation

            yield endpoint, schema_kwargs


class GraphQLField(metaclass=SchemaFieldRegistry):
    pass
