from daglib.task import Task


def test_task_init(function_factory):
    foo = function_factory["foo"]
    bar = function_factory["bar"]
    bazz = function_factory["bazz"]

    dag_name = "example_dag"
    dag_description = "This is an example DAG"
    run_id = "12345"
    profile = False
    profile_dir = "example/path/"

    task = Task(dag_name, dag_description, run_id, profile, profile_dir, bar)
    assert task.fn() == bar()
    assert task.name == "bar"
    assert task.inputs == ()

    task = Task(dag_name, dag_description, run_id, profile, profile_dir, bazz)
    assert task.fn(1, 2) == bazz(1, 2)
    assert task.name == "bazz"
    assert task.inputs == ("foo", "bar")

    task = Task(dag_name, dag_description, run_id, profile, profile_dir, foo, (0, 1, "foo"))
    assert task.fn() == foo()
    assert task.name == "foo"
    assert task.inputs == (0, 1, "foo")

    task = Task(dag_name, dag_description, run_id, profile, profile_dir, bazz, (0, 1, "foo"))
    assert task.fn(1, 2) == bazz(1, 2)
    assert task.name == "bazz"
    assert task.inputs == (0, 1, "foo")

    task = Task(dag_name, dag_description, run_id, profile, profile_dir, foo, suffix="0")
    assert task.fn() == foo()
    assert task.name == "foo 0"
    assert task.inputs == ()

    task = Task(dag_name, dag_description, run_id, profile, profile_dir, foo, name_override="oof")
    assert task.fn() == foo()
    assert task.name == "oof"
    assert task.inputs == ()
