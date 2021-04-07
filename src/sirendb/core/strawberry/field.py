from __future__ import annotations

from collections import OrderedDict
import functools
import inspect
import typing

import strawberry
from strawberry.field import StrawberryField

from .paginate import Paginated, Paginate


@strawberry.type
class NullField:
    ok: bool = strawberry.field(
        description='This will be irrelevant at some point.'
    )


@strawberry.field(description='TODO')
def null_query(self) -> NullField:
    strawberry.field(description='TODO')
    return NullField(ok=True)


class PaginatedFieldMeta(type):
    def __new__(meta, name, bases, namespace):
        print(f'\n\nPaginatedFieldMeta: {meta=} {name=} {bases=} {namespace=}\n\n')
        cls = type.__new__(meta, name, bases, namespace)
        # strawberry_cls = strawberry.field(cls)
        return cls


class PaginatedField(metaclass=PaginatedFieldMeta):
    def __init__(self, method):
        print(f'\n\n PaginatedField: {self=}\n {method=}\n\n')
        self.method = method
        self.method_name = method.__name__
        pass

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)


def paginated_field(func=None, node=None):
    if func is None:
        return functools.partial(paginated_field, node=node)

    assert node
    field = PaginatedField(func)
    field.node = node
    return field


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

                # Since Strawberry does not have any support for relays,
                # we have to implement pagination ourselves. To make things
                # simple to implement, we override the resolver's annotations
                # as well as the resolver itself to implement pagination with
                # dynamically created sorters via enums.
                def paginated_request(*args, **kwargs):
                    query = value.method(*args, **kwargs)
                    return Paginated.paginate(query, **kwargs)

                # Make the wrapper impersonate the actual resolver
                paginated_request.__name__ = value.method_name
                paginated_request.__annotations__ = {
                    'paginate': typing.Optional[Paginate],
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
