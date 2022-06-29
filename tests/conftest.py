from typing import Callable

import pytest


@pytest.fixture
def function_factory() -> dict[str, Callable]:
    def foo():
        return 1

    def bar():
        return 2

    def bazz(foo, bar):
        return foo + bar

    def mapper1(n):
        return n + 2

    def mapper2(n):
        return n * 2

    def joining(*mappings):
        return sum(mappings)

    def chunker(joining):
        return [joining] * 100

    def joining_final(*chunkers):
        sum(chunkers)

    return dict(
        foo=foo,
        bar=bar,
        bazz=bazz,
        mapper1=mapper1,
        mapper2=mapper2,
        joining=joining,
        chunker=chunker,
        joining_final=joining_final,
    )
