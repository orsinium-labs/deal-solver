
# stdlib
import typing

# external
import z3

# app
from ._layer import ExceptionInfo, Layer, ReturnInfo
from ._scope import Scope
from ._trace import Trace


if typing.TYPE_CHECKING:
    # app
    from .._proxies import BoolSort


class Context(typing.NamedTuple):
    # z3 context which should be used everywhere where z3 asks to use it.
    # Since z3 freaks out when we provide an explicit context
    # (supposedly, because we forget to pass it in some places),
    # this value is always None at the moment.
    z3_ctx: typing.Optional[z3.Context]

    # Scope holds z3 values for all variables executed up to the current line.
    scope: Scope

    # Given are checks that we don't validate but assume them to be always true.
    # For example, post-conditions of all functions the current function calls.
    given: Layer['BoolSort']

    # Expected are checks we do validate. For example, all `assert` statements.
    expected: Layer['BoolSort']

    exceptions: Layer[ExceptionInfo]    # all raised exceptions
    returns: Layer[ReturnInfo]          # all returned values

    # Trace is a collection of all function names in the current call stack.
    # It is used to mock recursive calls.
    trace: Trace

    # exceptions occured during evaluation
    skips: typing.List[Exception]

    # the user-provided function to extract contracts from called functions
    get_contracts: typing.Callable[[typing.Any], typing.Iterator]

    @classmethod
    def make_empty(cls, *, get_contracts, **kwargs) -> 'Context':
        obj = cls(
            z3_ctx=None,
            scope=Scope.make_empty(),
            given=Layer(),
            expected=Layer(),
            exceptions=Layer(),
            returns=Layer(),
            trace=Trace(),
            skips=[],
            get_contracts=get_contracts,
        )
        return obj.evolve(**kwargs)

    @property
    def interrupted(self) -> 'BoolSort':
        # app
        from .._proxies import BoolSort, or_expr
        false = BoolSort.val(False)
        return or_expr(
            false,
            *[exc.cond.as_bool for exc in self.exceptions],
            *[ret.cond.as_bool for ret in self.returns],
        )

    @property
    def return_value(self):
        returns = list(self.returns)
        if not returns:
            return None
        result = returns[0]
        for other in returns[1:]:
            result = result.merge(other)
        return result.value

    @property
    def evolve(self) -> typing.Callable[..., 'Context']:
        return self._replace

    def make_child(self) -> 'Context':
        return self.evolve(
            scope=self.scope.make_child(),
            given=self.given.make_child(),
            expected=self.expected.make_child(),
            exceptions=self.exceptions.make_child(),
            returns=self.returns.make_child(),
        )
