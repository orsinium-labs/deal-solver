# project
from deal_solver import Conclusion

# app
from .helpers import prove_f


def test_ok():
    theorem = prove_f("""
        @deal.post(lambda result: result == 0)
        def f(a: int) -> int:
            return a - a
    """)
    assert theorem.conclusion is Conclusion.OK


def test_fail():
    theorem = prove_f("""
        @deal.post(lambda result: result != 13)
        def f(a: int) -> int:
            return a
    """)
    assert theorem.conclusion is Conclusion.FAIL
    assert 'a = 13' in str(theorem.example)


def test_fail_1_out_of_2():
    theorem = prove_f("""
        @deal.post(lambda result: result >= 0)
        @deal.post(lambda result: result != 9)
        def f(a: int) -> int:
            return a ** 2
    """)
    assert theorem.conclusion is Conclusion.FAIL
    actual = str(theorem.example)
    assert 'a = 3' in actual or 'a = -3' in actual


def test_pre_post_condition_name_conflict():
    theorem = prove_f("""
        @deal.post(lambda a: a > 10)
        @deal.pre(lambda a: a > 5)
        @deal.pre(lambda a: a < 10)
        def f(a: int) -> int:
            return a * 2
    """)
    assert theorem.conclusion is Conclusion.OK


def test_post_condition_branching():
    theorem = prove_f("""
        @deal.post(lambda r: r >= 0)
        def f(a: int) -> int:
            if a > 0:
                return a
            else:
                return -a
    """)
    assert theorem.conclusion is Conclusion.OK


def test_post_condition_branching_no_else():
    theorem = prove_f("""
        @deal.post(lambda r: r >= 0)
        def f(a: int) -> int:
            if a > 0:
                return a
            return -a
    """)
    assert theorem.conclusion is Conclusion.OK


def test_post_condition_branching_many_branches():
    theorem = prove_f("""
        @deal.post(lambda r: r >= 0)
        def f(a: int) -> int:
            if a > 20:
                return a-20
            if a > 10:
                return a-10
            if a > 0:
                return a
            return -a
    """)
    assert theorem.conclusion is Conclusion.OK
