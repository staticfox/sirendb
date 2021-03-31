import typing

from flask_sqlalchemy import Model
import strawberry
from strawberry.field import StrawberryField


def _extract_sqlalchemy_orm_columns(model: Model) -> typing.Dict[str, StrawberryField]:
    fields = {}

    if not issubclass(model, Model):
        raise RuntimeError(
            'You set sqlalchemy_model but it was not an instance flask_sqlalchemy.Model'
        )

    table = model.__dict__['__table__']
    for column in table.columns:
        fields[column.key] = StrawberryField(
            python_name=column.key,
            graphql_name=column.key,
            type_=column.type.python_type,
            is_optional=column.nullable,
            description=column.doc,
            default_value=column.default,
        )

    return fields


class SchemaTypeMeta(type):
    def __new__(meta: 'SchemaTypeMeta', name: str, bases: tuple, namespace: dict) -> typing.Type:
        if not bases:
            return type.__new__(meta, name, bases, namespace)

        cls_name = str(name)
        cls_namespce = dict(namespace)

        # Description is set based on the following priority list:
        #   1) cls.Meta.description
        #   2) cls.__doc__
        #   3) cls.Meta.sqlalchemy_model.__doc__
        description = namespace.get('__doc__')

        if 'Meta' in namespace:
            Meta = namespace['Meta']

            if hasattr(Meta, 'name'):
                cls_name = Meta.name

            if hasattr(Meta, 'sqlalchemy_model'):
                fields = _extract_sqlalchemy_orm_columns(Meta.sqlalchemy_model)
                cls_namespce.setdefault('__annotations__', {})
                for field_name, field_value in fields.items():
                    if field_name in cls_namespce:
                        continue

                    cls_namespce['__annotations__'][field_name] = field_value.type
                    cls_namespce[field_name] = field_value

                model_doc = Meta.sqlalchemy_model.__dict__.get('__doc__')
                if model_doc and not description:
                    description = model_doc

            if getattr(Meta, 'description', None):
                description = Meta.description

        if description is not None:
            description = description.strip().rstrip()

        cls = type.__new__(meta, name, (object,), cls_namespce)
        straberry_cls = strawberry.type(
            cls,
            name=cls_name,
            description=description,
        )

        # Alphabetically sort fields so they're easy to find
        # within the documentation.
        straberry_cls._type_definition._fields = sorted(
            straberry_cls._type_definition._fields,
            key=lambda field: field.graphql_name
        )
        return straberry_cls


class SchemaTypeBase(metaclass=SchemaTypeMeta):
    pass
