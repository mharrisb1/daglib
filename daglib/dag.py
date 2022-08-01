import uuid
from typing import Any, Callable, Dict, List, Tuple

import networkx as nx
from dask.delayed import Delayed
from dask.optimization import cull

from daglib.node import Node


class Dag:
    def __init__(self, name: str = uuid.uuid4().hex, description: str = "") -> None:
        self.name = "".join(x for x in name if x.isalnum()).lower()
        self.description = description
        self._nodes_by_name: Dict[str, Node] = {}
        self.nxg = nx.DiGraph()

    @property
    def run_id(self) -> str:
        return f"run_{uuid.uuid1().hex}"

    def register_task(self, fn: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        node = Node(fn)
        self._nodes_by_name[node.name] = node
        return fn

    def task(self) -> Any:
        def register(fn: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
            return self.register_task(fn)

        return register

    def build_graph(self) -> None:
        edges = [(self._nodes_by_name[arg.name], node) for node in self._nodes_by_name.values() for arg in node.args]
        self.nxg = nx.DiGraph(edges)

    @property
    def dsk(self) -> Dict[Any, Tuple[Any, ...]]:
        return {node.name: tuple([node.fn, *[arg.name for arg in node.args]]) for node in nx.topological_sort(self.nxg)}

    @property
    def keys(self) -> List[str]:
        return [node.name for node in self.nxg.nodes if not list(self.nxg.successors(node))]

    def materialize(self, to_step: str | Callable[[Any, Any], Any] | None = None, optimize: bool = False) -> Delayed:
        self.build_graph()
        keys: List[str] | str = self.keys
        if len(keys) == 1:
            keys = keys[0]
        dsk = self.dsk
        if to_step:
            if callable(to_step):
                keys = to_step.__name__
            optimize = True
        if optimize:
            layers, _ = cull(dsk, keys)
        return Delayed(keys, dsk)

    def run(self, to_step: str | Callable[[Any, Any], Any] | None = None, optimize: bool = False) -> Any:
        return self.materialize(to_step, optimize).compute()

    # noinspection PyShadowingBuiltins
    def visualize(
        self,
        to_step: str | Callable[[Any, Any], Any] | None = None,
        optimize: bool = False,
        filename: str | None = None,
        format: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self.materialize(to_step, optimize).visualize(filename, format, **kwargs)
