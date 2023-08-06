from typing import Generator, Iterable


def cumsum(a: Iterable) -> Generator:
    """
    the cumalative sum starting from 0
    """
    agg = 0
    yield agg
    for i in a:
        agg += i
        yield agg


def stagger(a: Iterable) -> Generator:
    """
    yield pairs of the newest and second newest
    """
    it = iter(a)

    old = next(it)
    for new in it:
        yield old, new
        old = new
