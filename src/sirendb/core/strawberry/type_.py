import typing

from flask_sqlalchemy import Model
import strawberry
from strawberry.field import StrawberryField

from .scalars import (
    LimitedStringScalar,
    StringLimitExceeded,
)


def _extract_sqlalchemy_orm_columns(model: Model) -> typing.Dict[str, StrawberryField]:
    fields = {}

    if not issubclass(model, Model):
        raise RuntimeError(
            'You set sqlalchemy_model but it was not an instance flask_sqlalchemy.Model'
        )

    table = model.__dict__['__table__']
    for column in table.columns:
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

            def parse_value(value, _max_length=max_length):
                if len(value) > _max_length:
                    raise StringLimitExceeded
                return value

            type_._scalar_definition.parse_value = parse_value

            # So people are aware when they read the docs.
            if description is None:
                description = ''
            description += f' String size may not exceed {max_length} characters.'

        fields[column.key] = StrawberryField(**{
            'python_name': column.key,
            'graphql_name': column.key,
            'type_': type_,
            'is_optional': column.nullable,
            'default_value': column.default,
            'description': description,
        })

    return fields


class SchemaTypeMeta(type):
    def __new__(meta: 'SchemaTypeMeta', name: str, bases: tuple, namespace: dict) -> typing.Type:
        '''
        Sweetens strawberry.type with the following features:

        * Ability to extend the type's fields using a SQLAlchemy database model
        * Adds the ability to set the description from the class's docstring
        * Sorts the type's fields in alphabetical order for easy searching
        '''
        if not bases:
            return type.__new__(meta, name, bases, namespace)

        cls_name = str(name)
        cls_namespce = dict(namespace)
        cls_namespce.setdefault('__annotations__', {})

        # Description is set based on the following priority list:
        #   1) cls.Meta.description
        #   2) cls.__doc__
        #   3) cls.Meta.sqlalchemy_model.__doc__
        description = namespace.get('__doc__')

        cls_name = namespace.get('__typename__', cls_name)

        if 'Meta' in namespace:
            Meta = namespace['Meta']

            if hasattr(Meta, 'name'):
                cls_name = Meta.name

            if hasattr(Meta, 'sqlalchemy_model'):
                fields = _extract_sqlalchemy_orm_columns(Meta.sqlalchemy_model)
                only_fields = getattr(Meta, 'sqlalchemy_only_fields', ())
                for field_name, field_value in fields.items():
                    if field_name in cls_namespce or field_name not in only_fields:
                        continue

                    cls_namespce['__annotations__'][field_name] = field_value.type
                    cls_namespce[field_name] = field_value

                model_doc = Meta.sqlalchemy_model.__dict__.get('__doc__')
                if model_doc and not description:
                    description = model_doc

            if hasattr(Meta, 'node'):
                if not namespace.get('__isinput__') or not getattr(Meta, 'only_fields', None):
                    raise RuntimeError(
                        'Meta.node has only been tested with __isinput__ and only_fields. '
                        'Feel free to remove this check and proceed at your own risk.'
                    )
                for field_name in Meta.only_fields:
                    if field_name in cls_namespce:  # ??
                        continue
                    cls_namespce[field_name] = Meta.node.__dataclass_fields__[field_name]
                    cls_namespce['__annotations__'][field_name] = Meta.node.__annotations__[field_name]

            if getattr(Meta, 'description', None):
                description = Meta.description

        if description is not None:
            description = description.strip().rstrip()

        # This sorts the namespace & annotations so that the fields
        # without default values appear before the ones with default
        # values. This is required so that dataclass can initialize
        # the class without raising a exception:
        #
        # >>> TypeError: non-default argument 'email' follows default argument
        #

        without_default = []
        with_default = []

        for field_name, field_value in cls_namespce.items():
            if not isinstance(field_value, StrawberryField):
                continue

            if field_value.default_value:
                with_default.append((field_name, field_value))
            else:
                without_default.append((field_name, field_value))

        # without_default.sort(key=lambda pair: pair[0])
        # with_default.sort(key=lambda pair: pair[0])

        # Python 3.7+ guarentees that the built-in dict class
        # will retain insertion order, so an OrderedDict is
        # not needed.
        new_cls_namespce = {}
        new_cls_annotations = {}

        # Insert fields without default values first.
        for pair in without_default:
            new_cls_namespce[pair[0]] = pair[1]

        # Insert fields with default values after.
        for pair in with_default:
            new_cls_namespce[pair[0]] = pair[1]

        old_annotations = dict(cls_namespce['__annotations__'])
        # Since new_cls_namespce is correctly sorted, we can re-apply
        # the annotations in the same order.
        for key, value in new_cls_namespce.items():
            new_cls_annotations[key] = old_annotations[key]

        # Add the annotations then re-add the rest of the namespace.
        new_cls_namespce['__annotations__'] = new_cls_annotations

        for key, value in cls_namespce.items():
            if key in new_cls_namespce:
                continue
            new_cls_namespce[key] = value

        # GraphQL treats input types different from regular types.
        if namespace.get('__isinput__') is True:
            strawberry_type = strawberry.input
        else:
            strawberry_type = strawberry.type

        # Setup our Strawberry type so dataclass is happy.
        cls = type.__new__(meta, name, (object,), new_cls_namespce)
        straberry_cls = strawberry_type(
            cls,
            name=cls_name,
            description=description,
        )

        # Now that everything has been created properly, we can
        # re-order the type definition so fields will be sent
        # to GraphQL in alphabetical order.
        straberry_cls._type_definition._fields = sorted(
            straberry_cls._type_definition._fields,
            key=lambda field: field.graphql_name
        )
        return straberry_cls


class GraphQLType(metaclass=SchemaTypeMeta):
    pass
