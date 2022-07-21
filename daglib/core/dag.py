from __future__ import annotations

import uuid
from typing import Any, Callable, Iterable, TypeVar

import numpy as np
from dask.delayed import Delayed
from dask.optimization import cull

from daglib.core.task import Task
from daglib.exceptions import TaskBuildError

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])
Asset = TypeVar("Asset", bound=Task)


def chunk(arr: Iterable[Any], n: int) -> list[list[Any]]:
    return [list(sub) for sub in np.array_split(list(arr), n)]


def get(chunked_arr: list[list[Any]], i: int) -> list[Any]:
    try:
        return chunked_arr[i]
    except IndexError:
        return []


def find_keys(search_str: str, layers: dict[str, tuple[Any, ...]]) -> list[str] | str:
    keys = list(layers.keys())
    keys = list(filter(lambda k: k.split(" ")[0] == search_str, keys))
    if len(keys) > 1:
        return list(filter(lambda k: len(k.split(" ")) > 1 and "chunk" not in k.split(" "), keys))
    return keys[0]


def format_dag_name(s: str) -> str:
    return "".join(x for x in s if x.isalpha()).lower()


class Dag:
    def __init__(
        self,
        name: str | None = None,
        description: str = "",
        profile: bool = False,
    ) -> None:
        if not name:
            name = format_dag_name(str(uuid.uuid4()))
        self.name = format_dag_name(name)
        self.description = description
        self.profile = profile
        self.profile_dir = "meta/profiling/"
        self.run_id = "run_" + str(uuid.uuid1()).replace("-", "")[:9]
        self._tasks: list[Task] = []
        self._keys: list[str] = []

    def _register_task(
        self,
        fn: WrappedFn,
        inputs: Any | Iterable[Any] = (),
        suffix: str | None = None,
        final: bool = False,
        name_override: str | None = None,
        depends_on: list[WrappedFn | str] | None = None,
    ) -> Task:
        if depends_on:
            inputs = [*inputs, *[t.__name__ if callable(t) else t for t in depends_on]]
        task = Task(
            self.name, self.description, self.run_id, self.profile, self.profile_dir, fn, inputs, suffix, name_override
        )
        self._tasks.append(task)
        if final:
            self._keys.append(task.name)
        return task

    def _register_map_to_task(
        self,
        fn: WrappedFn,
        final: bool = False,
        joins: str | WrappedFn | None = None,
        map_to: list[Any] | str | WrappedFn | None = None,
        result_chunks: int | None = None,
        depends_on: list[WrappedFn | str] | None = None,
    ) -> None:
        if not map_to:
            map_to = []
        if joins:
            raise TaskBuildError("Task cannot have both map_to and joins specified. Choose one")
        if result_chunks:
            raise TaskBuildError("Task cannot have both map_to and result_chunks specified. Choose one")
        if callable(map_to):
            map_to = map_to.__name__
        if isinstance(map_to, str):
            map_to = [t.name for t in self._tasks if t.name.split(" ")[0] == map_to and len(t.name.split(" ")) > 1]
        for i, v in enumerate(map_to):
            self._register_task(fn, v, str(i), final, None, depends_on)

    def _register_joining_task(
        self,
        fn: WrappedFn,
        final: bool = False,
        joins: str | WrappedFn | None = None,
        map_to: list[Any] | str | WrappedFn | None = None,
        depends_on: list[WrappedFn | str] | None = None,
    ) -> Task:
        if map_to:
            raise TaskBuildError("Task cannot have both joins and map_to specified. Choose one")
        if callable(joins):
            joins = joins.__name__
        joined_tasks = [t.name for t in self._tasks if t.name.split(" ")[0] == joins and len(t.name.split(" ")) > 1]
        return self._register_task(fn, joined_tasks, None, final, None, depends_on)

    def _register_chunked_task(
        self,
        fn: WrappedFn,
        final: bool = False,
        joins: str | WrappedFn | None = None,
        map_to: list[Any] | str | WrappedFn | None = None,
        result_chunks: int | None = None,
        depends_on: list[WrappedFn | str] | None = None,
    ) -> None:
        if result_chunks is not None:
            if map_to:
                raise TaskBuildError("Task cannot have both result_chunks and map_to specified. Choose one")
            if joins:
                task = self._register_joining_task(fn, False, joins, None)
            else:
                task = self._register_task(fn, depends_on=depends_on)
            chunk_task = self._register_task(
                chunk, (task.name, result_chunks), task.name, depends_on=depends_on
            )  # type: ignore
            for n in range(result_chunks):
                self._register_task(get, (chunk_task.name, n), str(n), final, task.name, depends_on)  # type: ignore

    def task(
        self,
        final: bool = False,
        joins: str | WrappedFn | None = None,
        map_to: list[Any] | str | WrappedFn | None = None,
        result_chunks: int | None = None,
        depends_on: list[WrappedFn | str] | None = None,
    ) -> Callable[[WrappedFn], Callable[[WrappedFn], WrappedFn]]:
        def register(fn: WrappedFn) -> WrappedFn:
            if joins and not result_chunks:
                self._register_joining_task(fn, final, joins, map_to, depends_on)
            if map_to:
                self._register_map_to_task(fn, final, joins, map_to, result_chunks, depends_on)
            if result_chunks:
                self._register_chunked_task(fn, final, joins, map_to, result_chunks, depends_on)
            if not any([joins, map_to, result_chunks]):
                self._register_task(fn, (), None, final, None, depends_on)
            return fn

        return register

    @property
    def layers(self) -> dict[str, tuple[Any, ...]]:  # pragma: no cover
        layers = {task.name: tuple([task.fn, *task.inputs]) for task in self._tasks}
        return layers

    @property
    def final_tasks(self) -> list[str]:
        return self._keys

    def materialize(self, to_step: str | Callable[..., Any] | None = None, optimize: bool = False) -> Delayed:
        keys = self._keys[0] if len(self._keys) == 1 else self._keys
        layers = self.layers
        if to_step:
            if callable(to_step):
                to_step = to_step.__name__
            keys = find_keys(to_step, layers)
            optimize = True
        if optimize:
            layers, _ = cull(layers, keys)
        return Delayed(keys, layers)

    def add_subdag(self, other: Dag, keep_finals: bool = False) -> None:
        self._tasks += other._tasks
        if keep_finals:
            self._keys += other._keys

    def add_asset(self, asset: Asset) -> None:
        self._tasks.append(asset)

    def run(self, to_step: str | Callable[..., Any] | None = None, optimize: bool = False) -> Any:
        return self.materialize(to_step, optimize).compute()

    # noinspection PyShadowingBuiltins
    def visualize(
        self,
        to_step: str | Callable[..., Any] | None = None,
        optimize: bool = False,
        filename: str | None = None,
        format: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self.materialize(to_step, optimize).visualize(filename, format, **kwargs)
