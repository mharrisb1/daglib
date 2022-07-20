from daglib.task import Task


def test_task_init(function_factory):
    foo = function_factory["foo"]
    bar = function_factory["bar"]
    bazz = function_factory["bazz"]

    task = Task(bar)
    assert task.fn() == bar()
    assert task.name == "bar"
    assert task.inputs == ()

    task = Task(bazz)
    assert task.fn(1, 2) == bazz(1, 2)
    assert task.name == "bazz"
    assert task.inputs == ("foo", "bar")

    task = Task(foo, (0, 1, "foo"))
    assert task.fn() == foo()
    assert task.name == "foo"
    assert task.inputs == (0, 1, "foo")

    task = Task(bazz, (0, 1, "foo"))
    assert task.fn(1, 2) == bazz(1, 2)
    assert task.name == "bazz"
    assert task.inputs == (0, 1, "foo")

    task = Task(foo, suffix="0")
    assert task.fn() == foo()
    assert task.name == "foo 0"
    assert task.inputs == ()

    task = Task(foo, name_override="oof")
    assert task.fn() == foo()
    assert task.name == "oof"
    assert task.inputs == ()
