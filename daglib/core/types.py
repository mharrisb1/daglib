from typing import Any, TypeVar, Callable
from dataclasses import dataclass

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any], covariant=True)


@dataclass
class FnInput:
    name: str
    type: type | None
    default: Any | None
