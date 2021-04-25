from __future__ import annotations

from dataclasses import MISSING
from enum import Enum
import functools
import inspect
from logging import getLogger
import typing

from flask_sqlalchemy import Model
from graphql.pyutils.convert_case import camel_to_snake
from sqlalchemy import inspect as sql_inspect
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.schema import Column
import strawberry
from strawberry.ast import ast_from_info, LabelMap
from strawberry.enum import EnumDefinition
from strawberry.field import StrawberryField
from strawberry.types.info import Info
from strawberry.types.types import TypeDefinition
from strawberry.utils.str_converters import to_camel_case

from .scalars import (
    LimitedStringScalar,
    StringLimitExceeded,
)

# TODO: move this to sqlalchemy.py
table_to_type = {}
type_info_map = {}

log = getLogger('sirendb.core.strawberry.type')


class MissingFieldError(RuntimeError):
    pass


def _column_to_field(column: Column) -> StrawberryField:
    type_ = column.type.python_type
    description = column.doc
    if description is not None:
        description = description.strip().rstrip()

    if issubclass(type_, Enum):
        enum = Enum(type_.key, ' '.join([
            key
            for key in type_.__members__.keys()
        ]))
        enum.__doc__ = description
        return strawberry.enum(enum, description=description)

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

    return StrawberryField(**{
        'python_name': column.key,
        'graphql_name': to_camel_case(column.key),
        'type_': type_,
        'is_optional': column.nullable,
        'default_value': column.default,
        'description': description,
    })


def _generate_field_kwargs(relationship: RelationshipProperty):
    if relationship.target.name not in table_to_type:
        # This should exist by now. If it doesn't then someone forgot
        # to import the corresponding type.
        raise RuntimeError(
            f'_relationship_to_field called for {relationship.target.name} '
            'but it was not in the type table. Did you forget to create and '
            'import a GraphQLType with sqlalchemy_model specified?'
        )

    type_ = table_to_type[relationship.target.name]
    field_kwargs = {
        'python_name': relationship.key,
        'graphql_name': to_camel_case(relationship.key),
        'child': type_,
        'description': relationship.doc,
    }
    if relationship.uselist:
        field_kwargs.update({
            'is_list': True,
            'is_optional': False,
            'default_factory': [],
            'type_': typing.List[type_],
        })
    else:
        field_kwargs.update({
            'is_list': False,
            'is_optional': any([c.nullable for c in relationship.local_columns]),
            'type_': type_,
        })
    return field_kwargs


def _relationship_to_field(relationship: RelationshipProperty):
    if relationship.target.name not in table_to_type:
        return lambda: StrawberryField(**_generate_field_kwargs(relationship))

    field_kwargs = _generate_field_kwargs(relationship)
    return StrawberryField(**field_kwargs)


def _enum_to_field(column: Column, cls_name: str):
    enum_name = to_camel_case(cls_name + column.key.capitalize())
    enum_fields = ' '.join([
        key
        for key in column.type.python_type.__members__.keys()
    ])
    enum = Enum(enum_name, enum_fields)
    enum.__doc__ = column.doc
    rv = strawberry.enum(enum, description=column.doc)
    rv.description = column.doc
    rv.__doc__ = column.doc
    return rv


def _extract_sqlalchemy_orm_columns(
    model: Model,
    cls_name: str,
    only_fields: typing.Tuple[str] = (),
) -> typing.Dict[str, StrawberryField]:
    fields = {}

    if not issubclass(model, Model):
        raise RuntimeError(
            'You set sqlalchemy_model but it was not an instance flask_sqlalchemy.Model'
        )

    table = model.__dict__['__table__']
    for column in table.columns:
        if only_fields and column.key not in only_fields:
            continue

        if issubclass(column.type.python_type, Enum):
            fields[column.key] = _enum_to_field(column, cls_name)
        else:
            fields[column.key] = _column_to_field(column)

    mapper = sql_inspect(model)
    for relationship in mapper.relationships:
        if only_fields and relationship.key not in only_fields:
            continue
        fields[relationship.key] = _relationship_to_field(relationship)

    return fields


def _sqlalchemy_column_required(
    cls: GraphQLType,
    column_name: str,
):
    column = getattr(cls.Meta.sqlalchemy_model, column_name, None)
    if column and hasattr(column, 'nullable'):
        return column.nullable is False

    datafield_required = True
    data_fields = cls.__dict__['__dataclass_fields__']
    if column_name in data_fields:
        datafield = data_fields[column_name]
        if not hasattr(datafield, 'is_optional') and hasattr(datafield, 'type'):
            datafield_required = datafield.type.is_optional is False
        else:
            datafield_required = datafield.is_optional is False
    return datafield_required


def _resolve_sqlalchemy_result(
    cls: GraphQLType,
    type_info: dict,
    row: Model,
    request_document: LabelMap,
):
    namespace = {}

    columns = [
        (key, value)
        for key, value in type_info['without_default']
    ]
    columns.extend([
        (key, value)
        for key, value in type_info['with_default'].items()
    ])

    for column_name, field_cls in columns:
        if column_name in type_info['with_resolver']:
            continue

        datafield_required = _sqlalchemy_column_required(cls, column_name)

        column_request_document = None
        for field in request_document:
            if isinstance(field, list) and len(field) > 1:
                if field[0] == column_name and isinstance(field[1], list):
                    column_request_document = field[1]
            elif field == column_name:
                column_request_document = [column_name]

        if not datafield_required and column_request_document is None:
            log.debug(f'SKIP: {column_name}')
            continue

        value = getattr(row, column_name)
        if not value:
            namespace[column_name] = value
            continue

        if column_request_document and column_request_document != [column_name]:
            assert isinstance(request_document, list)

            log.debug(f'TYPE: {column_name} = {value} ... resolving')
            if isinstance(value, list):
                namespace[column_name] = []
                sub_table_name = value[0].__table__.name
                for sub_row in value:
                    namespace[column_name].append(_resolve_sqlalchemy_result(
                        cls=table_to_type[sub_table_name],
                        type_info=type_info_map[sub_table_name],
                        row=sub_row,
                        request_document=column_request_document,
                    ))
            else:
                sub_table_name = value.__table__.name
                namespace[column_name] = _resolve_sqlalchemy_result(
                    cls=table_to_type[sub_table_name],
                    type_info=type_info_map[sub_table_name],
                    row=value,
                    request_document=column_request_document,
                )

            log.debug(f'TYPE: {column_name} = {namespace[column_name]}')
        else:
            namespace[column_name] = value
            log.debug(f'SCALAR: {column_name} = {value}')

    for column_name, (field_value, missing_default) in type_info['with_resolver'].items():
        datafield_required = _sqlalchemy_column_required(cls, column_name)

        column_request_document = None
        for index, field in enumerate(request_document):
            if isinstance(field, list) and len(field) > 1:
                if field[0] == column_name and isinstance(field[1], list):
                    column_request_document = field[1]
            elif field == column_name:
                column_request_document = [column_name]
                if index + 1 < len(request_document):
                    if isinstance(request_document[index + 1], list):
                        column_request_document = request_document[index + 1]

        if not datafield_required and column_request_document is None:
            log.debug(f'SKIP: {column_name}')
            continue

        resolver_name = 'resolve_' + column_name
        method = getattr(cls, resolver_name)

        return_type = method.__annotations__['return']
        if hasattr(return_type, '__origin__'):
            return_type, *_ = typing.get_args(method.__annotations__['return'])

        log.debug(f'RESOLVE: {column_name} = {row} ... resolving')
        if hasattr(return_type, 'Meta'):
            return_type_info = type_info_map[return_type.Meta.sqlalchemy_model.__table__.name]
            namespace[column_name] = method(
                cls=return_type,
                type_info=return_type_info,
                row=row,
                request_document=column_request_document or request_document,
            )
        else:
            namespace[column_name] = method(
                cls=return_type,
                type_info=None,
                row=row,
                request_document=column_request_document or request_document,
            )
        log.debug(f'RESOLVE: {column_name} = {namespace[column_name]}')

    ordered_keys = inspect.getfullargspec(cls.__dict__['__init__']).args
    for index, key in enumerate(ordered_keys):
        if index > 0 and key not in namespace:
            field = type_info['with_default'].get(key)
            datafield_required = _sqlalchemy_column_required(cls, key)

            if not field and datafield_required:
                raise MissingFieldError(
                    f'{cls.Meta.name}.{key} is required but was not provided by {row} {namespace.keys()}'
                )

            if field and hasattr(field.type, '__origin__'):
                namespace[key] = []
            else:
                namespace[key] = None

            log.debug(f'DEFAULT: {key} = {namespace[key]}')

    return cls.ordered_args(namespace)


def is_valid_field(item) -> bool:
    # typing.List
    if getattr(item, '__origin__', None) is list:
        # TODO: This should only have 1 element, enforce it?
        return is_valid_field(item.__args__[0])

    if inspect.isclass(item):
        if issubclass(item, StrawberryField):
            return True

        type_def = getattr(item, '_enum_definition', None)
        if isinstance(type_def, EnumDefinition):
            return True

        type_def = getattr(item, '_type_definition', None)
        if isinstance(type_def, TypeDefinition):
            return True
    else:
        if isinstance(item, StrawberryField):
            return True

    return False


class SchemaTypeMeta(type):
    def __new__(meta: 'SchemaTypeMeta', name: str, bases: tuple, namespace: dict) -> typing.Type:
        '''
        Sweetens strawberry.type with the following features:

        * Ability to extend the type's fields using a SQLAlchemy database model
        * Adds the ability to set the description from the class's docstring
        * Sorts the type's fields in alphabetical order for easy searching
        '''
        if not hasattr(meta, 'types'):
            meta.types = {}

        if not hasattr(meta, 'late_resolvers'):
            meta.late_resolvers = []

        if not bases:
            return type.__new__(meta, name, bases, namespace)

        cls_name = str(name)
        cls_namespace = dict(namespace)
        cls_namespace.setdefault('__annotations__', {})

        # Description is set based on the following priority list:
        #   1) cls.Meta.description
        #   2) cls.__doc__
        #   3) cls.Meta.sqlalchemy_model.__doc__
        description = namespace.get('__doc__')

        cls_name = namespace.get('__typename__', cls_name)
        sqlalchemy_model = None

        if 'Meta' in namespace:
            Meta = namespace['Meta']

            if hasattr(Meta, 'name'):
                cls_name = Meta.name

            if hasattr(Meta, 'sqlalchemy_model'):
                sqlalchemy_model = Meta.sqlalchemy_model
                only_fields = getattr(Meta, 'sqlalchemy_only_fields', ())
                fields = _extract_sqlalchemy_orm_columns(
                    model=sqlalchemy_model,
                    cls_name=cls_name,
                    only_fields=only_fields,
                )
                for field_name, field_value in fields.items():
                    if field_name in cls_namespace:
                        continue

                    if hasattr(field_value, 'type'):
                        cls_namespace['__annotations__'][field_name] = field_value.type
                    else:
                        cls_namespace['__annotations__'][field_name] = field_value

                    cls_namespace[field_name] = field_value

                model_doc = sqlalchemy_model.__dict__.get('__doc__')
                if model_doc and not description:
                    description = model_doc

            if hasattr(Meta, 'node'):
                if not namespace.get('__isinput__') or not getattr(Meta, 'only_fields', None):
                    raise RuntimeError(
                        'Meta.node has only been tested with __isinput__ and only_fields. '
                        'Feel free to remove this check and proceed at your own risk.'
                    )
                for field_name in Meta.only_fields:
                    if field_name in cls_namespace:  # ??
                        continue
                    cls_namespace[field_name] = Meta.node.__dataclass_fields__[field_name]
                    cls_namespace['__annotations__'][field_name] = Meta.node.__annotations__[field_name]

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
        with_default = {}
        with_resolver = {}

        for field_name, field_value in cls_namespace.items():
            field_value_name = getattr(field_value, '__name__', '')
            is_late_resolver = bool(
                callable(field_value) and field_value_name == '<lambda>'
            )

            inner_field_name = None
            if field_name.startswith('resolve_'):
                inner_field_name = field_name[8:]

            if not inner_field_name and not is_valid_field(field_value) and not is_late_resolver:
                continue

            if is_late_resolver:
                meta.late_resolvers.append((field_name, field_value, cls_name))

            default = getattr(field_value, 'default', None)
            default_factory = getattr(field_value, 'default_factory', None)

            missing_default = default is MISSING and default_factory is MISSING

            if inner_field_name:
                with_resolver[inner_field_name] = (field_value, missing_default)
                continue

            if missing_default:
                without_default.append((field_name, field_value))
            else:
                with_default[field_name] = field_value

        # print(f'{with_default=} {without_default=}')
        # without_default.sort(key=lambda pair: pair[0])
        # with_default.sort(key=lambda pair: pair[0])

        # Python 3.7+ guarentees that the built-in dict class
        # will retain insertion order, so an OrderedDict is
        # not needed.
        new_cls_namespace = {}
        new_cls_annotations = {}

        # Insert fields without default values first.
        for field_name, field_value in without_default:
            new_cls_namespace[field_name] = field_value

        # Insert fields with default values after.
        for field_name, field_value in with_default.items():
            new_cls_namespace[field_name] = field_value

        old_annotations = dict(cls_namespace['__annotations__'])
        # Since new_cls_namespace is correctly sorted, we can re-apply
        # the annotations in the same order.
        for key, value in new_cls_namespace.items():
            new_cls_annotations[key] = old_annotations[key]

        # Add the annotations then re-add the rest of the namespace.
        new_cls_namespace['__annotations__'] = new_cls_annotations

        for key, value in cls_namespace.items():
            if key in new_cls_namespace:
                continue
            new_cls_namespace[key] = value

        # # Drop in resolvers now
        for key, (value, missing_default) in with_resolver.items():
            assert key in new_cls_namespace['__annotations__'], f'{key} not in namespace!'
            new_cls_namespace['resolve_' + key] = value

        # GraphQL treats input types different from regular types.
        if namespace.get('__isinput__') is True:
            strawberry_type = strawberry.input
        else:
            strawberry_type = strawberry.type

        # Setup our Strawberry type so dataclass is happy.
        cls = type.__new__(meta, name, (object,), new_cls_namespace)
        straberry_cls = strawberry_type(
            cls,
            name=cls_name,
            description=description,
        )

        straberry_cls.ordered_args = functools.partial(
            _ordered_args, straberry_cls
        )

        straberry_cls.from_sqlalchemy_model = functools.partial(
            _from_sqlalchemy_model, straberry_cls
        )

        # Now that everything has been created properly, we can
        # re-order the type definition so fields will be sent
        # to GraphQL in alphabetical order.
        straberry_cls._type_definition._fields = sorted(
            straberry_cls._type_definition._fields,
            key=lambda field: field.graphql_name
        )

        # Add it to our table cache
        if sqlalchemy_model:
            table_to_type[sqlalchemy_model.__table__.name] = straberry_cls
            type_info_map[sqlalchemy_model.__table__.name] = {
                'without_default': without_default,
                'with_default': with_default,
                'with_resolver': with_resolver,
            }

        meta.types[cls_name] = straberry_cls
        return straberry_cls

    @classmethod
    def resolve_lambdas(meta):
        # Since a some types rely on each other, there's a good chance
        # that dependency A may not exist when dependency B call for it.
        # To circumvent this, we allow types to be lambdas so the types
        # can be resolved once schema initialization actually takes place.
        # Here we walk through each type and resolve it since everything
        # should have already been imported by now.
        for field_name, resolver, cls_name in meta.late_resolvers:
            strawberry_cls = meta.types[cls_name]

            # strawberry_cls.__dict__ in itself is a mappingproxy,
            # so item assignment won't work here.
            setattr(strawberry_cls, field_name, resolver())

            # but everything within the mappingproxy itself does.
            strawberry_cls.__dict__['__annotations__'][field_name] = resolver()
            strawberry_cls.__dict__['__dataclass_fields__'][field_name].type = resolver()
            for index, field in enumerate(strawberry_cls.__dict__['_type_definition']._fields):
                if field.name == field_name:
                    strawberry_cls.__dict__['_type_definition']._fields[index] = resolver()

        for table_name, options in type_info_map.items():
            for key, value in options['with_default'].items():
                if callable(value) and getattr(value, '__name__', '') == '<lambda>':
                    type_info_map[table_name]['with_default'][key] = value()


def _ordered_args(cls, result: typing.Dict[str, typing.Any]):
    args = []
    for key in cls.__annotations__.keys():
        args.append(result[key])
    return cls(*args)


def _from_sqlalchemy_model(cls, result, info: Info, request_document: LabelMap = None):
    if result == []:
        return []
    elif not result:
        return None

    table_name = cls.Meta.sqlalchemy_model.__table__.name
    type_info = type_info_map[table_name]
    this_field_name = camel_to_snake(cls.Meta.name)

    if not request_document:
        ast = ast_from_info(info)
        request_document = ast.document_python_names[0]
        document_field_name = camel_to_snake(info.field_name)
        document_field_index = request_document.index(document_field_name)
        request_document = request_document[document_field_index + 1]

        this_field_index = request_document.index(this_field_name)
        request_document = request_document[this_field_index + 1]

    log.debug(f'from_sqlalchemy_model {cls.Meta.name} {type(result).__name__}')
    if isinstance(result, list):
        return [
            _resolve_sqlalchemy_result(
                cls=cls,
                type_info=type_info,
                row=resolved_row,
                request_document=request_document,
            )
            for resolved_row in result
        ]

    return _resolve_sqlalchemy_result(
        cls=cls,
        type_info=type_info,
        row=result,
        request_document=request_document,
    )


class GraphQLType(metaclass=SchemaTypeMeta):
    pass
