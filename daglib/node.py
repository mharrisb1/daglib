from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple


@dataclass
class Arg:
    name: str
    type: type | None
    default: Any | None


class Node:
    def __init__(self, fn: Callable[[Any, Any], Any]) -> None:
        self._fn = fn
        self._name = self._fn.__name__

    @property
    def fn(self) -> Callable[[Any, Any], Any]:
        return self._fn

    def set_fn(self, fn: Callable[[Any, Any], Any]) -> None:
        self._fn = fn

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    @property
    def description(self) -> str | None:
        return self.fn.__doc__

    @property
    def annotations(self) -> Dict[str, type]:
        # noinspection PyUnresolvedReferences
        return self.fn.__annotations__

    @property
    def is_annotated(self) -> bool:
        return bool(self.annotations)

    @property
    def return_type(self) -> type | None:
        return self.annotations.get("return")

    @property
    def defaults(self) -> Tuple[Any, ...]:
        return tuple(reversed(self.fn.__defaults__)) if self.fn.__defaults__ else tuple()  # type: ignore

    @property
    def has_defaults(self) -> bool:
        return bool(self.defaults)

    @property
    def args(self) -> List[Arg]:
        # noinspection PyUnresolvedReferences
        args = [Arg(n, None, None) for n in self.fn.__code__.co_varnames[: self.fn.__code__.co_argcount]]

        for arg in args:
            arg.type = self.annotations.get(arg.name)

        if self.has_defaults:
            for i, d in enumerate(self.defaults):
                args[len(args) - 1 - i].default = d

        return args

    @property
    def has_args(self) -> bool:
        return bool(self.args)

    def __repr__(self) -> str:
        return self.name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)  # type: ignore
