from dataclasses import MISSING
from enum import Enum
from logging import getLogger
from typing import (
    Any,
    Dict,
    Tuple,
    Optional,
    List,
)

from flask_sqlalchemy import Model
from graphql.pyutils.convert_case import camel_to_snake
from sqlalchemy import inspect as sql_inspect

from .type_ import table_to_type

log = getLogger('sirendb.core.strawberry.sqlalchemy')

def _resolve_keys(type_) -> Tuple[Dict[str, Any], set]:
    keys_with_resolvers = {}
    keys_without_resolvers = set()

    for field in type_._type_definition.fields:
        resolver_name = f'resolve_{field.name}'

        if resolver_name in type_.__dict__:
            keys_with_resolvers[field.name] = getattr(type_, resolver_name)
        else:
            keys_without_resolvers.add(field.name)

    return keys_with_resolvers, keys_without_resolvers


class TypeIsStillResolving:
    pass


def _resolve_row(
    row: Model,
    keyname: str,
    gql_ast_document: List[str],
    gql_ast_prefix: str,
    required_keys: List[str],
    late_resolvers: set,
    resolved_cache: Dict[str, Any],
    is_root: bool,
    visited_tables: List[str],
):
    dataclass_kwargs = {}

    if not hasattr(row, '__table__'):
        return row

    # if row.__table__.name == 'siren_media':
    #     breakpoint()

    target_type = table_to_type[row.__table__.name]
    type_name = camel_to_snake(target_type.Meta.name)
    table_cache_key = f'{row.__table__.name}.{row.id}'
    if table_cache_key in resolved_cache:
        if row.__table__.name == 'siren_media':
            log.debug(f'returning value {resolved_cache[table_cache_key]}')
        return resolved_cache[table_cache_key]

    default_values = {}
    type_required_keys = []
    for field in target_type._type_definition.fields:
        if field.is_optional:
            continue

        if field.default is not MISSING or field.default_factory is not MISSING:
            continue

        uses_column = False
        for column in row.__table__.columns:
            if column.key == field.name:
                uses_column = getattr(column, 'uselist', False)
                break

        if not uses_column:
            mapper = sql_inspect(target_type.Meta.sqlalchemy_model)
            for relationship in mapper.relationships:
                if relationship.key == field.name:
                    uses_column = getattr(relationship, 'uselist', False)
                    break

        if field.is_list and uses_column:
            default_values[field.name] = []
        else:
            type_required_keys.append(field.name)

    with_res, without_res = _resolve_keys(target_type)
    for key in without_res:
        key_name = type_name + '.' + key
        try:
            required_keys.remove(key_name)
        except ValueError:
            try:
                type_required_keys.remove(key)
            except ValueError:
                pass

        cache_key = f'{table_cache_key}.{key}'

        # if key in ('download_url', 'media_type'):
        #     breakpoint()
        #     print('222')

        if cache_key in resolved_cache:
            # log.debug(f'setting value {cache_key} {resolved_cache[cache_key]}')
            dataclass_kwargs[key] = resolved_cache[cache_key]
            continue

        value = getattr(row, key)
        if isinstance(value, list):
            dataclass_kwargs[key] = [
                _resolve_row(
                    row=i,
                    keyname=key,
                    gql_ast_document=gql_ast_document,
                    gql_ast_prefix=gql_ast_prefix,
                    required_keys=required_keys,
                    late_resolvers=late_resolvers,
                    resolved_cache=resolved_cache,
                    is_root=False,
                    visited_tables=visited_tables,
                )
                for i in value
            ]
        elif isinstance(value, Model):
            sub_target_table = table_to_type[row.__table__.name]
            sub_type_name = camel_to_snake(sub_target_table.Meta.name)

            target_table_key = '.' + sub_type_name + '.'

            if target_table_key in visited_tables:
                continue

            visited_tables.append(target_table_key)

            key_name = sub_type_name + '.' + key
            try:
                required_keys.remove(key_name)
            except ValueError:
                try:
                    type_required_keys.remove(key)
                except ValueError:
                    pass
            # if keyname == 'model':
            #     breakpoint()
            #     print('')
            #     print('')
            dataclass_kwargs[key] = _build_dataclass(
                type_=sub_target_table,
                node=row,
                gql_ast_document=gql_ast_document,
                gql_ast_prefix=gql_ast_prefix,
                late_resolvers=late_resolvers,
                resolved_cache=resolved_cache,
                is_root=False,
                required_keys=required_keys,
                visited_tables=visited_tables,
            )
            # if value is None:
            #     breakpoint()
            #     print('')
            #     print('')
        else:
            dataclass_kwargs[key] = value
        # if isinstance(dataclass_kwargs[key], Enum):
        #     breakpoint()
            # dataclass_kwargs[key] = dataclass_kwargs[key].name
        resolved_cache[cache_key] = dataclass_kwargs[key]

    for key, resolver in with_res.items():
        key_name = type_name + '.' + key
        try:
            required_keys.remove(key_name)
        except ValueError:
            try:
                type_required_keys.remove(key)
            except ValueError:
                pass

        cache_key = f'{table_cache_key}.{key}'
        if cache_key in resolved_cache:
            # log.debug(f'setting value {cache_key} {resolved_cache[cache_key]}')
            dataclass_kwargs[key] = resolved_cache[cache_key]
            continue
            # SUS: this doesnt work

        dataclass_kwargs[key] = resolver(
            self=row,
            gql_ast_document=gql_ast_document,
            gql_ast_prefix=gql_ast_prefix,
            required_keys=required_keys,
            late_resolvers=late_resolvers,
            resolved_cache=resolved_cache,
            is_root=False,
            visited_tables=visited_tables,
        )
        resolved_cache[cache_key] = dataclass_kwargs[key]

    if 'previous_locations' in dataclass_kwargs:
        from sirendb.v1.types.siren_location import SirenLocationNode
        assert isinstance(dataclass_kwargs['previous_locations'], list)
        for itemitem in dataclass_kwargs['previous_locations']:
            assert isinstance(itemitem, SirenLocationNode), f'expected SirenLocationNode got {itemitem}'
        # assert isinstance()

    new_dataclass_kwargs = {}

    ordered_keys = target_type.__annotations__.keys() #  [field.name for field in target_type._type_definition._fields]
    for key in ordered_keys:
        if key in new_dataclass_kwargs:
            continue

        if key not in dataclass_kwargs:
            if key in default_values:
                new_dataclass_kwargs[key] = default_values[key]
            continue

    for key in target_type.__annotations__.keys():
        new_dataclass_kwargs[key] = dataclass_kwargs[key]
    rv = target_type(**new_dataclass_kwargs)

    for dict_key in rv.__dict__.keys():
        field = getattr(rv, dict_key)
        if callable(field) and dict_key in new_dataclass_kwargs:
            rv.__dict__[dict_key] = new_dataclass_kwargs[dict_key]
        elif callable(field):
            rv.__dict__[dict_key] = field()

    log.debug(rv.__dict__)    
    

    resolved_cache[table_cache_key] = rv
    return rv


def _build_dataclass(
    type_,
    node: Model,
    gql_ast_document: List[str],
    gql_ast_prefix: str,
    late_resolvers: Optional[set] = None,
    resolved_cache: Optional[Dict[str, Any]] = None,
    is_root: Optional[bool] = None,
    required_keys: Optional[List[str]] = None,
    visited_tables: Optional[List[str]] = None,
):
    if late_resolvers is None:
        late_resolvers = set()

    if resolved_cache is None:
        resolved_cache = {}

    type_name = camel_to_snake(type_.Meta.name)
    module, actual_node = gql_ast_prefix.split('.', -1)
    if required_keys is None:
        required_keys = []
        for field_name in gql_ast_document:
            if not field_name.startswith(gql_ast_prefix):
                continue
            trimmed = field_name.removeprefix(module + '.')
            if not trimmed.startswith(actual_node):
                continue
            required_keys.append(trimmed)
        required_keys.sort()

    if visited_tables is None:
        visited_tables = []

    keys_with_resolvers, keys_without_resolvers = _resolve_keys(type_)
    dataclass_kwargs = {}
    table_cache_key = f'{node.__table__.name}.{node.id}'

    table_key = '.' + type_name + '.'

    if table_key in visited_tables:
        return None

    visited_tables.append(table_key)

    type_required_keys = []

    default_values = {}
    for field in type_._type_definition.fields:
        if field.is_optional:
            continue

        if field.default is not MISSING or field.default_factory is not MISSING:
            continue

        uses_column = False

        for column in node.__table__.columns:
            if column.key == field.name:
                uses_column = getattr(column, 'uselist', False)
                break
        if not uses_column:
            mapper = sql_inspect(type_.Meta.sqlalchemy_model)
            for relationship in mapper.relationships:
                if relationship.key == field.name:
                    uses_column = getattr(relationship, 'uselist', False)
                    break

        if field.is_list and uses_column:
            default_values[field.name] = []
        else:
            type_required_keys.append(field.name)

    # breakpoint()

    for key in keys_without_resolvers:
        item = getattr(node, key)
        # breakpoint()

        key_name = type_name + '.' + key
        try:
            required_keys.remove(key_name)
        except ValueError:
            try:
                type_required_keys.remove(key)
            except ValueError:
                continue

        cache_key = f'{table_cache_key}.{key}'
        if cache_key in resolved_cache:
            # log.debug(f'setting value {cache_key} {resolved_cache[cache_key]}')
            dataclass_kwargs[key] = resolved_cache[cache_key]
            continue


        if isinstance(item, list):
            dataclass_kwargs[key] = [
                _resolve_row(
                    row=i,
                    keyname=key,
                    gql_ast_document=gql_ast_document,
                    gql_ast_prefix=gql_ast_prefix,
                    required_keys=required_keys,
                    late_resolvers=late_resolvers,
                    resolved_cache=resolved_cache,
                    is_root=is_root is None,
                    visited_tables=visited_tables,
                )
                for i in item
            ]
        else:
            dataclass_kwargs[key] = _resolve_row(
                row=item,
                keyname=key,
                gql_ast_document=gql_ast_document,
                gql_ast_prefix=gql_ast_prefix,
                required_keys=required_keys,
                late_resolvers=late_resolvers,
                resolved_cache=resolved_cache,
                is_root=is_root is None,
                visited_tables=visited_tables,
            )

        resolved_cache[cache_key] = dataclass_kwargs[key]

    for key, resolver in keys_with_resolvers.items():
        key_name = type_name + '.' + key
        try:
            required_keys.remove(key_name)
        except ValueError:
            try:
                type_required_keys.remove(key)
            except ValueError:
                pass

        cache_key = f'{table_cache_key}.{key}'
        if cache_key in resolved_cache:
            # log.debug(f'setting value {cache_key} {resolved_cache[cache_key]}')
            dataclass_kwargs[key] = resolved_cache[cache_key]
            continue

        # if visited_tables:
        #     breakpoint()

        dataclass_kwargs[key] = resolver(
            self=node,
            gql_ast_document=gql_ast_document,
            gql_ast_prefix=gql_ast_prefix,
            required_keys=required_keys,
            late_resolvers=late_resolvers,
            resolved_cache=resolved_cache,
            is_root=is_root is None,
            visited_tables=visited_tables,
        )
        resolved_cache[cache_key] = dataclass_kwargs[key]

    # sort dataclass
    new_dataclass_kwargs = {}

    # for key, default_value in default_values.items():
    #     if key in new_dataclass_kwargs:
    #         continue

    #     new_dataclass_kwargs[key] = default_value

    # This will be in order
    ordered_keys = list(type_.__annotations__.keys()) # [field.name for field in type_._type_definition._fields]
    for key in ordered_keys:
        if key in new_dataclass_kwargs:
            continue

        if key not in dataclass_kwargs:
            if key in default_values:
                new_dataclass_kwargs[key] = default_values[key]
            continue

        # Didn't want or need this field
        try:
            new_dataclass_kwargs[key] = dataclass_kwargs[key]
        except KeyError as exc:
            print(exc)
            breakpoint()
            print('')
            print('')
    # if 'previous_locations' in new_dataclass_kwargs and new_dataclass_kwargs['previous_locations'] is None:
    #     breakpoint()

    # breakpoint()

    try:
        rv = type_(*list(new_dataclass_kwargs.values()))
    except TypeError as exc:
        print(exc)
        breakpoint()
        print('')
        print('')

    for dict_key in rv.__dict__.keys():
        field = getattr(rv, dict_key)
        if callable(field) and dict_key in new_dataclass_kwargs:
            rv.__dict__[dict_key] = new_dataclass_kwargs[dict_key]
        elif callable(field):
            rv.__dict__[dict_key] = field()
    
    log.debug(rv.__dict__)

    try:
        assert isinstance(rv.__dict__['street_pitch'], float)
    except AssertionError:
        print('')
        breakpoint()
        print('')
        print('')
    except KeyError:
        pass

    try:
        assert isinstance(rv.__dict__['media'], list)
    except AssertionError:
        print('')
        breakpoint()
        print('')
        print('')
    except KeyError:
        pass

    return rv
