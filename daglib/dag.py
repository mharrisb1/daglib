from __future__ import annotations

from typing import Any, Callable, Iterable

import numpy as np
from dask.delayed import Delayed
from dask.optimization import cull

from daglib.task import Task


class TaskBuildError(Exception):
    pass


def chunk(arr: Iterable[Any], n: int) -> list[list[Any]]:
    return [list(sub) for sub in np.array_split(arr, n)]


def get(chunked_arr: list[list[Any]], i: int) -> list[Any]:
    return chunked_arr[i]


class Dag:
    def __init__(self, name: str | None = None, description: str | None = None) -> None:
        self.name = name
        self.description = description
        self.tasks: list[Task] = []
        self.keys: list[str] = []

    def _register_task(
        self,
        fn: Callable[..., Any],
        inputs: Any | Iterable[Any] = (),
        suffix: str | None = None,
        final: bool = False,
        name_override: str | None = None,
    ) -> Task:
        task = Task(fn, inputs, suffix, name_override)
        self.tasks.append(task)
        if final:
            self.keys.append(task.name)
        return task

    def _register_map_to_task(
        self,
        fn: Callable[..., Any],
        final: bool = False,
        joins: str | None = None,
        map_to: list[Any] | str | None = None,
        result_chunks: int | None = None,
    ) -> None:
        if map_to is None:
            map_to = []
        if joins:
            raise TaskBuildError("Task cannot have both map_to and joins specified")
        if result_chunks:
            raise TaskBuildError
        if isinstance(map_to, str):
            map_to = [t.name for t in self.tasks if t.name.split(" ")[0] == map_to]
        for i, v in enumerate(map_to):
            self._register_task(fn, v, str(i), final)

    def _register_joining_task(
        self,
        fn: Callable[..., Any],
        final: bool = False,
        joins: str | None = None,
        map_to: list[Any] | str | None = None,
    ) -> Task:
        if map_to:
            raise TaskBuildError
        joined_tasks = [t.name for t in self.tasks if t.name.split(" ")[0] == joins and len(t.name.split(" ")) > 1]
        return self._register_task(fn, joined_tasks, None, final)

    def _register_chunked_task(
        self,
        fn: Callable[..., Any],
        final: bool = False,
        joins: str | None = None,
        map_to: list[Any] | str | None = None,
        result_chunks: int | None = None,
    ) -> None:
        if result_chunks is None:
            result_chunks = 1
        if map_to:
            raise TaskBuildError
        if joins:
            task = self._register_joining_task(fn, False, joins, None)
        else:
            task = self._register_task(fn)
        chunk_task = self._register_task(chunk, (task.name, result_chunks), task.name)
        for n in range(result_chunks):
            self._register_task(get, (chunk_task.name, n), str(n), final, task.name)

    def task(
        self,
        final: bool = False,
        joins: str | None = None,
        map_to: list[Any] | str | None = None,
        result_chunks: int | None = None,
    ) -> Callable[..., Any]:
        def register(fn: Callable[..., Any]) -> Callable[..., Any]:
            if joins and not result_chunks:
                self._register_joining_task(fn, final, joins, map_to)
            if map_to:
                self._register_map_to_task(fn, final, joins, map_to, result_chunks)
            if result_chunks:
                self._register_chunked_task(fn, final, joins, map_to, result_chunks)
            if not any([joins, map_to, result_chunks]):
                self._register_task(fn, (), None, final)
            return fn

        return register

    @property
    def layers(self) -> dict[str, tuple[Any, ...]]:  # pragma: no cover
        layers = {task.name: tuple([task.fn, *task.inputs]) for task in self.tasks}
        return layers

    def materialize(self, to_step: str | None = None, optimize: bool = False) -> Delayed:
        keys = self.keys[0] if len(self.keys) == 1 else self.keys
        layers = self.layers
        if to_step:
            keys = to_step
            optimize = True
        if optimize:
            layers, _ = cull(layers, keys)
        return Delayed(keys, layers)

    def add_subdag(self, other: Dag | list[Dag]) -> None:
        if not isinstance(other, Iterable):
            other = [other]
        for dag in other:
            self.tasks += dag.tasks
            self.keys += dag.keys