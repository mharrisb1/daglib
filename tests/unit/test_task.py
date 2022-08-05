from daglib import Task, Arg


def test_arg_constructor():
    arg = Arg("foo")
    assert arg.name == "foo"
    assert arg.type is None
    assert arg.default is None

    arg = Arg("bar", int)
    assert arg.name == "bar"
    assert arg.type == int
    assert arg.default is None

    arg = Arg("bazz", default=3)
    assert arg.name == "bazz"
    assert arg.type is None
    assert arg.default == 3

    arg = Arg("fizz", int, 3)
    assert arg.name == "fizz"
    assert arg.type == int
    assert arg.default == 3


def test_task_constructed_from_object():
    obj = "foo"

    task = Task.from_object(obj, "foo")

    assert task.name == "foo"
    assert task() == "foo"
