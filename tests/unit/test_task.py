from daglib import Task


def test_task_constructed_from_object():
    obj = "foo"

    task = Task.from_object(obj, "foo")

    assert task.name == "foo"
    assert task() == "foo"
