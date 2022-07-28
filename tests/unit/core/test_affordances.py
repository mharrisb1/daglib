from daglib.core.types import FnInput
from daglib.core.affordances import FnCallProxying, FnDeconstructing


def bar():
    print("")


def foo(a, b):
    """This is a docstring"""
    return a + str(b)


def typed_bar() -> None:
    print("")


def typed_foo(a: str, b: int) -> str:
    return a + str(b)


def typed_foo_with_defaults(a: str, b: int = 1, c: int = 2) -> str:
    return a + str(b) + str(c)


def test_call_function_through_proxy():
    fn = FnCallProxying(foo)
    assert fn("a", 1) == "a1"


def test_get_name_from_fn():
    fn = FnDeconstructing(bar)
    assert fn.name == "bar"


def test_get_doc_from_fn():
    fn = FnDeconstructing(bar)
    assert fn.doc is None

    fn = FnDeconstructing(foo)
    assert fn.doc == "This is a docstring"


def test_get_annotations_from_fn():
    fn = FnDeconstructing(bar)
    assert fn.annotations == {}
    assert not fn.is_annotated

    fn = FnDeconstructing(typed_bar)
    assert fn.annotations == {"return": None}
    assert fn.is_annotated

    fn = FnDeconstructing(foo)
    assert fn.annotations == {}
    assert not fn.is_annotated

    fn = FnDeconstructing(typed_foo)
    assert fn.annotations == {"a": str, "b": int, "return": str}
    assert fn.is_annotated


def test_get_return_type():
    fn = FnDeconstructing(bar)
    assert fn.return_type is None
    assert not fn.is_annotated

    fn = FnDeconstructing(foo)
    assert fn.return_type is None
    assert not fn.is_annotated

    fn = FnDeconstructing(typed_bar)
    assert fn.return_type is None
    assert fn.is_annotated

    fn = FnDeconstructing(typed_foo)
    assert fn.return_type == str
    assert fn.is_annotated


def test_get_inputs_from_fn():
    fn = FnDeconstructing(bar)
    assert fn.inputs == []
    assert not fn.has_inputs

    fn = FnDeconstructing(foo)
    assert fn.inputs == [FnInput("a", None, None), FnInput("b", None, None)]
    assert fn.has_inputs

    fn = FnDeconstructing(typed_foo)
    assert fn.inputs == [FnInput("a", str, None), FnInput("b", int, None)]
    assert fn.has_inputs

    fn = FnDeconstructing(typed_foo_with_defaults)
    print(fn.inputs)
    assert fn.inputs == [FnInput("a", str, None), FnInput("b", int, 1), FnInput("c", int, 2)]
    assert fn.has_inputs
