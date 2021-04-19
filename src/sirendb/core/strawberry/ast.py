from collections.abc import Iterable

from graphql.pyutils.convert_case import camel_to_snake

from sirendb.utils.debug import ASSERT


def _parse_ast_inner(node, fragments: dict, prefix: str = None):
    parsed = []

    if node.kind == 'inline_fragment' and node.selection_set:
        for selection in node.selection_set.selections:
            parsed.extend(_parse_ast_inner(selection, fragments, prefix))
    elif node.kind == 'fragment_definition'and node.selection_set:
        for selection in node.selection_set.selections:
            parsed.extend(_parse_ast_inner(selection, fragments, prefix))
    elif node.kind == 'field':
        if prefix:
            new_prefix = prefix + node.name.value
        else:
            new_prefix = node.name.value

        new_prefix = camel_to_snake(new_prefix)

        if node.selection_set:
            for selection in node.selection_set.selections:
                parsed.extend(_parse_ast_inner(selection, fragments, new_prefix + '.'))
        else:
            assert '..' not in new_prefix
            parsed.append(new_prefix)
    elif node.kind == 'fragment_spread':
        if prefix:
            new_prefix = prefix
        else:
            new_prefix = ''

        new_prefix = camel_to_snake(new_prefix)

        for name in fragments[node.name.value]:
            assert '..' not in new_prefix
            parsed.append(new_prefix + name)
    else:
        ASSERT(False, f'Got unknown node type {node.kind}')

    return parsed


def ast_to_dict(node, fragments: dict, prefix: str = None):
    parsed = []

    if isinstance(node, Iterable):
        for item in node:
            parsed.extend(_parse_ast_inner(item, fragments))
    else:
        parsed = _parse_ast_inner(node, fragments)

    return parsed
