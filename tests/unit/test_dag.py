import pytest
from dask.delayed import Delayed

from daglib.dag import TaskBuildError, chunk, get, Dag, find_keys


def test_chunk():
    arr = [1, 2, 3, 4, 5, 6]
    assert chunk(arr, 2) == [[1, 2, 3], [4, 5, 6]]


def test_get():
    arr = [1, 2, 3, 4, 5, 6]
    chunked_arr = chunk(arr, 2)
    assert get(chunked_arr, 0) == [1, 2, 3]
    assert get(chunked_arr, 1) == [4, 5, 6]


def test_find_keys():
    layers = {"foo": (1, 2, 3), "foo 1": (1, 2, 3), "foo 2": (1, 2, 3), "bar": ()}
    assert find_keys("foo", layers) == ["foo 1", "foo 2"]


def test_dag_init():
    dag = Dag()
    assert dag._tasks == []
    assert dag._keys == []
    assert dag.layers == {}

    dag = Dag("dag name", "this is a dag description")
    assert dag.name == "dagname"
    assert dag.description == "this is a dag description"
    assert dag._tasks == []
    assert dag._keys == []
    assert dag.layers == {}


def test_register_task(function_factory):
    foo = function_factory["foo"]
    bar = function_factory["bar"]
    bazz = function_factory["bazz"]

    dag = Dag()
    dag._register_task(foo)
    dag._register_task(bar)
    dag._register_task(bazz)
    assert len(dag._tasks) == 3

    dag = Dag()
    dag._register_task(bazz, inputs=(1, 2))
    assert dag._tasks[0].inputs == (1, 2)

    dag = Dag()
    dag._register_task(bazz, suffix="0")
    assert dag._tasks[0].name == "bazz 0"

    dag = Dag()
    dag._register_task(bazz, final=True)
    assert dag._keys == ["bazz"]
    assert dag._tasks[0].inputs == ("foo", "bar")

    dag = Dag()
    dag._register_task(bazz, name_override="fizz")
    assert dag._tasks[0].name == "fizz"

    dag = Dag()
    dag._register_task(bazz, inputs=(1, 2), suffix="0", final=True, name_override="fizz")
    assert dag._tasks[0].name == "fizz 0"
    assert dag._tasks[0].inputs == (1, 2)
    assert dag._keys == ["fizz 0"]


def test_register_mapping_task(function_factory):
    mapper1 = function_factory["mapper1"]
    mapper2 = function_factory["mapper2"]

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
    assert len(dag._tasks) == 5
    assert dag._tasks[0].name == "mapper1 0"
    assert dag._tasks[1].name == "mapper1 1"
    assert dag._tasks[2].name == "mapper1 2"
    assert dag._tasks[3].name == "mapper1 3"
    assert dag._tasks[4].name == "mapper1 4"

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
    dag._register_map_to_task(fn=mapper2, map_to="mapper1")
    assert len(dag._tasks) == 10
    assert dag._tasks[5].name == "mapper2 0"
    assert dag._tasks[6].name == "mapper2 1"
    assert dag._tasks[7].name == "mapper2 2"
    assert dag._tasks[8].name == "mapper2 3"
    assert dag._tasks[9].name == "mapper2 4"

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
    dag._register_map_to_task(fn=mapper2, map_to=mapper1)
    assert len(dag._tasks) == 10
    assert dag._tasks[5].name == "mapper2 0"
    assert dag._tasks[6].name == "mapper2 1"
    assert dag._tasks[7].name == "mapper2 2"
    assert dag._tasks[8].name == "mapper2 3"
    assert dag._tasks[9].name == "mapper2 4"

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5], final=True)
    assert len(dag._tasks) == 5
    assert len(dag._keys) == 5

    dag = Dag()
    with pytest.raises(TaskBuildError):
        dag._register_map_to_task(fn=mapper1, map_to="foo", joins="bar")

    dag = Dag()
    with pytest.raises(TaskBuildError):
        dag._register_map_to_task(fn=mapper1, map_to="foo", result_chunks=5)


def test_register_joining_task(function_factory):
    mapper1 = function_factory["mapper1"]
    joining = function_factory["joining"]

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
    dag._register_joining_task(fn=joining, joins="mapper1")
    assert len(dag._tasks) == 6
    assert dag._tasks[5].name == "joining"
    assert dag._tasks[5].inputs == ("mapper1 0", "mapper1 1", "mapper1 2", "mapper1 3", "mapper1 4")

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
    dag._register_joining_task(fn=joining, joins="mapper1", final=True)
    assert dag._keys == ["joining"]

    dag = Dag()
    dag._register_joining_task(fn=joining, joins="mapper1")
    assert dag._tasks[0].inputs == ()

    dag = Dag()
    dag._register_joining_task(fn=joining, joins=mapper1)
    assert dag._tasks[0].inputs == ()

    dag = Dag()
    with pytest.raises(TaskBuildError):
        dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
        dag._register_joining_task(fn=joining, joins="mapper1", map_to="mapper1")


def test_chunked_task(function_factory):
    mapper1 = function_factory["mapper1"]
    chunker = function_factory["chunker"]

    dag = Dag()
    dag._register_chunked_task(fn=chunker, result_chunks=2)
    assert len(dag._tasks) == 4
    assert dag._tasks[0].name == "chunker"
    assert dag._tasks[1].name == "chunk chunker"
    assert dag._tasks[2].name == "chunker 0"
    assert dag._tasks[3].name == "chunker 1"

    dag = Dag()
    dag._register_map_to_task(fn=mapper1, map_to=[1, 2, 3, 4, 5])
    dag._register_chunked_task(fn=chunker, joins="mapper1", result_chunks=2)
    assert len(dag._tasks) == 9

    dag = Dag()
    with pytest.raises(TaskBuildError):
        dag._register_chunked_task(fn=chunker, map_to="mapper1", result_chunks=2)

    dag = Dag()
    dag._register_chunked_task(fn=chunker, result_chunks=2, final=True)
    assert dag._keys == ["chunker 0", "chunker 1"]


def test_task_wrapper_simple():
    dag = Dag()

    @dag.task()
    def foo():
        return 1

    @dag.task()
    def bar():
        return 2

    @dag.task(final=True)
    def bazz(foo, bar):
        return foo + bar

    assert len(dag._tasks) == 3


def test_task_wrapper_complex():
    dag = Dag()

    @dag.task(map_to=[0, 1, 2, 3, 4, 5])
    def mapper1(n):
        return n + 2

    @dag.task(map_to="mapper1")
    def mapper2(n):
        return n * 2

    @dag.task(joins="mapper2")
    def joining(*mappings):
        return sum(mappings)

    @dag.task(result_chunks=2)
    def chunker(joining):
        return [joining] * 100

    @dag.task(joins="chunker", final=True)
    def joining_final(*chunkers):
        sum(chunkers)

    assert len(dag._tasks) == 18
    assert dag._keys == ["joining_final"]


def test_task_wrapper_invalid_combinations():
    dag = Dag()

    with pytest.raises(TaskBuildError):

        @dag.task(map_to=[0, 1, 2, 3, 4, 5], joins="foo")
        def mapper1(n):
            return n + 2

    with pytest.raises(TaskBuildError):

        @dag.task(map_to=[0, 1, 2, 3, 4, 5], result_chunks=2)
        def mapper1(n):
            return n + 2

    with pytest.raises(TaskBuildError):

        @dag.task(map_to="mapper1", joins="foo")
        def mapper2(n):
            return n * 2

    with pytest.raises(TaskBuildError):

        @dag.task(map_to="mapper1", result_chunks=2)
        def mapper2(n):
            return n * 2

    with pytest.raises(TaskBuildError):

        @dag.task(joins="mapper2", map_to="foo")
        def joining(*mappings):
            return sum(mappings)

    with pytest.raises(TaskBuildError):

        @dag.task(result_chunks=2, map_to="foo")
        def chunker(joining):
            return [joining] * 100

    with pytest.raises(TaskBuildError):

        @dag.task(joins="chunker", map_to="foo", final=True)
        def joining_final(*chunkers):
            sum(chunkers)


def test_materialize():
    dag = Dag()

    @dag.task()
    def foo():
        return 1

    @dag.task()
    def bar():
        return 2

    @dag.task()
    def never_computed(foo):
        return foo

    @dag.task(final=True)
    def bazz(foo, bar):
        return foo + bar

    assert isinstance(dag.materialize(), Delayed)

    assert dag.materialize()._key == "bazz"
    assert list(dag.materialize()._dask.keys()) == ["foo", "bar", "never_computed", "bazz"]

    assert dag.materialize(to_step="foo")._key == "foo"
    assert list(dag.materialize(to_step="foo")._dask.keys()) == ["foo"]

    assert dag.materialize(to_step=foo)._key == "foo"
    assert list(dag.materialize(to_step=foo)._dask.keys()) == ["foo"]

    assert dag.materialize(optimize=True)._key == "bazz"
    assert sorted(list(dag.materialize(optimize=True)._dask.keys())) == ["bar", "bazz", "foo"]


def test_add_subdag():
    dag1 = Dag()

    @dag1.task(final=True)
    def foo():
        return 1

    dag2 = Dag()

    @dag2.task(final=True)
    def bar():
        return 2

    dag1.add_subdag(dag2)

    assert len(dag1._tasks) == 2
    assert len(dag1._keys) == 2


def test_add_subdags_from_iterable():
    dag1 = Dag()

    @dag1.task(final=True)
    def foo():
        return 1

    dag2 = Dag()

    @dag2.task(final=True)
    def bar():
        return 2

    dag3 = Dag()

    @dag3.task(final=True)
    def fizz():
        return 3

    dag1.add_subdag([dag2, dag3])

    assert len(dag1._tasks) == 3
    assert len(dag1._keys) == 3
