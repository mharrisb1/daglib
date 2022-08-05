from daglib import Dag, Task


def test_add_subdag():
    dag1 = Dag()
    dag2 = Dag()

    def foo():
        return 1

    foo_task = Task.from_function(foo)

    def bar(foo):
        return foo * 3

    bar_task = Task.from_function(bar)

    def bazz(bar):
        return bar - 2

    bazz_task = Task.from_function(bazz)

    dag1.register_task(foo_task)
    dag1.register_task(bar_task)

    dag2.register_task(bazz_task)

    dag1.add_subdag(dag2)

    assert dag1._tasks_by_name == {"foo": foo_task, "bar": bar_task, "bazz": bazz_task}
