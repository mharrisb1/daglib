from __future__ import annotations

from typing import Any, Callable, Iterable

import numpy as np
from dask.delayed import Delayed
from dask.optimization import cull

from daglib.task import Task
from daglib.exceptions import TaskBuildError


def chunk(arr: Iterable[Any], n: int) -> list[list[Any]]:
    return [list(sub) for sub in np.array_split(arr, n)]


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


class Dag:
    def __init__(self, name: str | None = None, description: str | None = None) -> None:
        self.name = name
        self.description = description
        self._tasks: list[Task] = []
        self._keys: list[str] = []

    def _register_task(
        self,
        fn: Callable[..., Any],
        inputs: Any | Iterable[Any] = (),
        suffix: str | None = None,
        final: bool = False,
        name_override: str | None = None,
        wait_for: list[Callable[..., Any] | str] | None = None,
    ) -> Task:
        if wait_for:
            inputs = [*inputs, *[t.__name__ if callable(t) else t for t in wait_for]]
        task = Task(fn, inputs, suffix, name_override)
        self._tasks.append(task)
        if final:
            self._keys.append(task.name)
        return task

    def _register_map_to_task(
        self,
        fn: Callable[..., Any],
        final: bool = False,
        joins: str | Callable[..., Any] | None = None,
        map_to: list[Any] | str | Callable[..., Any] | None = None,
        result_chunks: int | None = None,
        wait_for: list[Callable[..., Any] | str] | None = None,
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
            self._register_task(fn, v, str(i), final, None, wait_for)

    def _register_joining_task(
        self,
        fn: Callable[..., Any],
        final: bool = False,
        joins: str | Callable[..., Any] | None = None,
        map_to: list[Any] | str | Callable[..., Any] | None = None,
        wait_for: list[Callable[..., Any] | str] | None = None,
    ) -> Task:
        if map_to:
            raise TaskBuildError("Task cannot have both joins and map_to specified. Choose one")
        if callable(joins):
            joins = joins.__name__
        joined_tasks = [t.name for t in self._tasks if t.name.split(" ")[0] == joins and len(t.name.split(" ")) > 1]
        return self._register_task(fn, joined_tasks, None, final, None, wait_for)

    def _register_chunked_task(
        self,
        fn: Callable[..., Any],
        final: bool = False,
        joins: str | Callable[..., Any] | None = None,
        map_to: list[Any] | str | Callable[..., Any] | None = None,
        result_chunks: int | None = None,
        wait_for: list[Callable[..., Any] | str] | None = None,
    ) -> None:
        if result_chunks is not None:
            if map_to:
                raise TaskBuildError("Task cannot have both result_chunks and map_to specified. Choose one")
            if joins:
                task = self._register_joining_task(fn, False, joins, None)
            else:
                task = self._register_task(fn)
            chunk_task = self._register_task(chunk, (task.name, result_chunks), task.name)
            for n in range(result_chunks):
                self._register_task(get, (chunk_task.name, n), str(n), final, task.name, wait_for)

    def task(
        self,
        final: bool = False,
        joins: str | Callable[..., Any] | None = None,
        map_to: list[Any] | str | Callable[..., Any] | None = None,
        result_chunks: int | None = None,
        wait_for: list[Callable[..., Any] | str] | None = None,
    ) -> Callable[..., Any]:
        def register(fn: Callable[..., Any]) -> Callable[..., Any]:
            if joins and not result_chunks:
                self._register_joining_task(fn, final, joins, map_to, wait_for)
            if map_to:
                self._register_map_to_task(fn, final, joins, map_to, result_chunks, wait_for)
            if result_chunks:
                self._register_chunked_task(fn, final, joins, map_to, result_chunks, wait_for)
            if not any([joins, map_to, result_chunks]):
                self._register_task(fn, (), None, final, None, wait_for)
            return fn

        return register

    @property
    def layers(self) -> dict[str, tuple[Any, ...]]:  # pragma: no cover
        layers = {task.name: tuple([task.fn, *task.inputs]) for task in self._tasks}
        return layers

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

    def add_subdag(self, other: Dag | list[Dag]) -> None:
        if not isinstance(other, Iterable):
            other = [other]
        for dag in other:
            self._tasks += dag._tasks
            self._keys += dag._keys

    def run(self, to_step: str | Callable[..., Any] | None = None, optimize: bool = False) -> Any:
        return self.materialize(to_step, optimize).compute()

    def visualize(
        self,
        to_step: str | Callable[..., Any] | None = None,
        optimize: bool = False,
        filename: str | None = None,
        format: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self.materialize(to_step, optimize).visualize(filename, format, **kwargs)
