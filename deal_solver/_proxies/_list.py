# stdlib
import typing

# external
import z3

# app
from ._funcs import random_name, unwrap, wrap
from ._proxy import ProxySort
from ._registry import registry


if typing.TYPE_CHECKING:
    # app
    from ._bool import BoolSort
    from ._int import IntSort


@registry.add
class ListSort(ProxySort):
    expr: z3.SeqRef
    type_name = 'list'

    def __init__(self, expr) -> None:
        # assert z3.is_seq(expr)
        assert not z3.is_string(expr)
        self.expr = expr

    @classmethod
    def make_empty(cls, sort: z3.SortRef = None) -> 'ListSort':
        expr = None
        if sort is not None:
            expr = cls.make_empty_expr(sort)
        return cls(expr=expr)

    @staticmethod
    def make_empty_expr(sort):
        return z3.Empty(z3.SeqSort(sort))

    @property
    def as_bool(self) -> 'BoolSort':
        if self.expr is None:
            return registry.bool.val(False)
        expr = z3.Length(self.expr) != z3.IntVal(0)
        return registry.bool(expr=expr)

    def get_item(self, index: 'ProxySort') -> 'ProxySort':
        return wrap(self.expr[unwrap(index)])

    def get_slice(self, start: 'ProxySort', stop: 'ProxySort') -> 'ProxySort':
        if self.expr is None:
            return self
        start_expr = unwrap(start)
        stop_expr = unwrap(stop)
        return wrap(z3.SubSeq(
            s=self.expr,
            offset=start_expr,
            length=stop_expr - start_expr,
        ))

    def append(self, item: z3.ExprRef) -> 'ListSort':
        cls = type(self)
        unit = z3.Unit(unwrap(item))
        self._ensure(item)
        return cls(expr=self.expr + unit)

    def contains(self, item: 'ProxySort') -> 'BoolSort':
        self._ensure(item)
        unit = z3.Unit(unwrap(item))
        return registry.bool(expr=z3.Contains(self.expr, unit))

    def index(self, other: 'ProxySort', start: 'ProxySort' = None) -> 'IntSort':
        if start is None:
            start = z3.IntVal(0)
        unit = z3.Unit(unwrap(other))
        return registry.int(expr=z3.IndexOf(self.expr, unit, unwrap(start)))

    @property
    def length(self) -> 'IntSort':
        if self.expr is None:
            return registry.int(expr=z3.IntVal(0))
        return registry.int(expr=z3.Length(self.expr))

    def count(self, item: 'ProxySort') -> 'IntSort':
        if self.expr is None:
            return registry.int(expr=z3.IntVal(0))
        item_expr = unwrap(item)
        f = z3.RecFunction(
            random_name('list_count'),
            z3.IntSort(), z3.IntSort(),
        )
        i = z3.Int(random_name('index'))
        one = z3.IntVal(1)
        zero = z3.IntVal(0)
        z3.RecAddDefinition(f, i, z3.If(
            i < zero,
            zero,
            f(i - one) + z3.If(self.expr[i] == item_expr, one, zero),
        ))
        result = f(z3.Length(self.expr) - one)
        return registry.int(result)
