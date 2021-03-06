"""Solver core for deal, powered by z3-solver.
"""
# app
from ._eval_contracts import Contract
from ._exceptions import ProveError, UnsupportedError
from ._theorem import Conclusion, Proof, Theorem


__version__ = '0.1.0'
__all__ = [
    'Theorem',
    'Conclusion',
    'Contract',
    'Proof',
    'UnsupportedError',
    'ProveError',
]
