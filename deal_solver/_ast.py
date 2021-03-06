# stdlib
from contextlib import suppress
from typing import Optional, Tuple

# external
import astroid


def get_name(expr) -> Optional[str]:
    if isinstance(expr, astroid.Name):
        return expr.name
    if isinstance(expr, astroid.Attribute):
        left = get_name(expr.expr)
        if left is None:
            return None
        return left + '.' + expr.attrname
    return None


def get_full_name(expr) -> Tuple[str, str]:
    if expr.parent is None:
        return '', expr.name

    if type(expr.parent) is astroid.Module:
        return expr.parent.qname(), expr.name

    if type(expr.parent) in (astroid.FunctionDef, astroid.UnboundMethod):
        module_name, func_name = get_full_name(expr=expr.parent)
        return module_name, func_name + '.' + expr.name

    if type(expr.parent) is astroid.ClassDef:
        module_name, class_name = get_full_name(expr=expr.parent)
        return module_name, class_name + '.' + expr.name

    path, _, func_name = expr.qname().rpartition('.')
    return path, func_name


def infer(expr) -> Tuple[astroid.node_classes.NodeNG, ...]:
    if not isinstance(expr, astroid.node_classes.NodeNG):
        return tuple()
    with suppress(astroid.exceptions.InferenceError, RecursionError):
        guesses = expr.infer()
        if guesses is astroid.Uninferable:  # pragma: no cover
            return tuple()
        return tuple(g for g in guesses if repr(g) != 'Uninferable')
    return tuple()
