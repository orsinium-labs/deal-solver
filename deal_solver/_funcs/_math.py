# stdlib
import math

# external
import z3

# app
from .._context import Context
from .._proxies import BoolSort, FloatSort, IntSort, ProxySort, and_expr, if_expr, wrap
from ._registry import FUNCTIONS, register


@register('math.isclose')
def math_isclose(left, right, rel_tol=None, abs_tol=None, *, ctx: Context, **kwargs) -> BoolSort:
    if not isinstance(left, FloatSort) and not isinstance(right, FloatSort):
        return left == right

    if isinstance(left, IntSort):
        left = left.as_float
    if isinstance(right, IntSort):
        right = right.as_float

    if rel_tol is None:
        rel_tol = FloatSort.val(1e-09)
    if abs_tol is None:
        abs_tol = FloatSort.val(0.0)

    if FloatSort.prefer_real:
        left = left.as_real
        right = right.as_real
    else:
        left = left.as_fp
        right = right.as_fp

    builtin_max = FUNCTIONS['builtins.max']
    abs_max = builtin_max(left.abs, right.abs, ctx=ctx)
    delta = builtin_max(rel_tol * abs_max, abs_tol, ctx=ctx)
    return if_expr(
        and_expr(left.is_nan, right.is_nan),
        BoolSort.val(True),
        (left - right).abs <= delta,
    )


@register('math.isinf')
def math_isinf(x, ctx: Context, **kwargs) -> BoolSort:
    if not isinstance(x, FloatSort):
        return BoolSort.val(False)
    if not x.is_fp:
        return BoolSort.val(False)
    return z3.fpIsInf(x.expr)


@register('math.isnan')
def math_isnan(x, ctx: Context, **kwargs) -> BoolSort:
    if not isinstance(x, FloatSort):
        return BoolSort.val(False)
    if not x.is_fp:
        return BoolSort.val(False)
    return BoolSort(expr=z3.fpIsNaN(x.expr, ctx=ctx.z3_ctx))


@register('math.sin')
def math_sin(x: ProxySort, ctx: Context, **kwargs) -> ProxySort:
    """Taylor's Series of sin x
    """
    if not isinstance(x, FloatSort):
        x = x.as_float

    series = [
        (False, 3),
        (True, 5),
        (False, 7),
        (True, 9),
        (False, 11),
    ]
    result: ProxySort = x
    nominator = x
    for positive, pow in series:
        nominator = nominator * x * x
        denominator = wrap(z3.IntVal(math.factorial(pow), ctx=ctx.z3_ctx))
        if positive:
            result += nominator / denominator
        else:
            result -= nominator / denominator
    return result


@register('math.trunc')
def math_trunc(x: ProxySort, ctx: Context, **kwargs) -> ProxySort:
    if not isinstance(x, FloatSort):
        return x.as_int
    return if_expr(
        x.as_int.as_float == x,
        x.as_int,
        if_expr(
            x > FloatSort.val(0, ctx=ctx.z3_ctx),
            x.as_int,
            x.as_int + IntSort.val(1),
        ),
    )
