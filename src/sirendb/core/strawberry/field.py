from collections import OrderedDict
import typing

import strawberry
from strawberry.field import StrawberryField


class SchemaFieldRegistry(type):
    def __new__(meta: 'SchemaFieldRegistry', name: str, bases: tuple, namespce: typing.Dict[str, typing.Any]):
        cls = type.__new__(meta, name, bases, namespce)

        if not hasattr(meta, 'registry'):
            meta.registry = {}

        if not bases:
            return cls

        if name not in ('Query', 'Mutation'):
            raise RuntimeError(
                'You subclassed GraphQLField but your class\'s name is neither\n'
                'Query nor Mutation. Rename your class or remove GraphQLField.'
            )

        meta.registry.setdefault(name, set()).add(cls)
        meta.registry[name] -= set(bases)

        return cls

    @classmethod
    def create_root_type(meta: 'SchemaFieldRegistry', type_name: str) -> typing.Type:
        namespce = {}
        namespce_class_map = {}
        for Class in meta.registry.get(type_name, ()):
            for attr_name, attr_value in Class.__dict__.items():
                # FIXME: One glaring issue with this approach is that now resolvers may not
                #        call member functions.
                # print(f'{Class.__name__}.{attr_name} {attr_value=}')
                if attr_name.startswith('_') or not isinstance(attr_value, StrawberryField):
                    continue
                if attr_name in namespce:
                    raise RuntimeError(
                        f'You tried to specify {Class.__module__}.{type_name}.{attr_name}\n'
                        f'but it is already defined in {namespce_class_map[attr_name].__module__}.{type_name}.\n'
                        'Remove or rename one of the entries.'
                    )
                namespce[attr_name] = attr_value
                namespce_class_map[attr_name] = Class

        # Alphabetically sort fields so they're easy to find
        # within the documentation.
        namespce = OrderedDict(sorted(namespce.items()))
        cls = type.__new__(type, type_name, (object,), namespce)
        return strawberry.type(cls, description=(
            f'The root {type_name} object for interacting with SirenDB\'s GraphQL API.'
        ))


class GraphQLField(metaclass=SchemaFieldRegistry):
    pass
