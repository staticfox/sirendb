from __future__ import annotations

from collections import OrderedDict
import inspect
import typing

import strawberry
from strawberry.field import StrawberryField
from strawberry.utils.str_converters import to_camel_case
import sqlalchemy as sa

from .paginate import Paginated, Paginate, PaginatedField, SortingEnum


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

    enum_name = to_camel_case(node.Meta.sqlalchemy_model.__table__.name.capitalize())
    sorter.make_enum(enum_name)
    return sorter


class SchemaFieldRegistry(type):
    def __new__(meta: 'SchemaFieldRegistry', name: str, bases: tuple, namespace: typing.Dict[str, typing.Any]):
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

                # Since Strawberry does not have any support for relays,
                # we have to implement pagination ourselves. To make things
                # simple to implement, we override the resolver's annotations
                # as well as the resolver itself to implement pagination with
                # dynamically created sorters via enums.
                def paginated_request(*args, **kwargs):
                    query = value.method(*args, **kwargs)
                    return Paginated.paginate(query, sorter=sorting_enum, **kwargs)

                # Make the wrapper impersonate the actual resolver
                paginated_request.__name__ = value.method_name
                paginated_request.__annotations__ = {
                    'paginate': typing.Optional[Paginate],
                    'sort': typing.Optional[sorting_enum.strawberry_enum],
                    'return': Paginated[value.node],
                }
                paginated_request.__signature__ = sig
                # HACKHACK: Strawberry will try to resolve the paginated type's
                #           python node. Since it's not defined within this scope,
                #           we have to export it to prevent a NameError.
                locals()[value.node.__name__] = value.node
                namespace[value.method_name] = strawberry.field(
                    paginated_request, description=value.method.__doc__
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
    def create_root_type(meta: 'SchemaFieldRegistry', type_name: str, endpoint: str) -> typing.Optional[typing.Type]:
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
    def schema_for_endpoint(meta: 'SchemaFieldRegistry') -> typing.Iterator[typing.Type]:
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
