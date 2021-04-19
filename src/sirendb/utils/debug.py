import inspect
import logging
from typing import NamedTuple

log = logging.getLogger('sirendb.core.strawberry.ast')


class Function(NamedTuple):
    module_name: str
    function_name: str
    lineno: int
    statement: str

    @property
    def python_path(self) -> str:
        return self.module_name + '.' + self.function_name


def _get_caller() -> Function:
    for index, frame in enumerate(inspect.stack()):
        if index == 0 or frame.function == 'ASSERT':
            continue

        module_path = str(frame.filename)
        idx = module_path.rfind('sirendb.')
        module_path = module_path[idx:]
        module_path = module_path[:-3]
        failing_assert_statement = ' '.join([ctx.strip() for ctx in frame.code_context])

        # TODO: interpolate variables
        return Function(
            module_name=module_path,
            function_name=frame.function,
            lineno=frame.lineno,
            statement=failing_assert_statement,
        )


def ASSERT(condition, message):
    if __debug__:
        assert condition, message

    if condition:
        return condition

    func = _get_caller()
    log2 = logging.getLogger(func.python_path)
    log2.error(
        f'assertion failed: {func.python_path}:{func.lineno}: {func.statement}',
        extra={'': ''}
    )

    return condition
