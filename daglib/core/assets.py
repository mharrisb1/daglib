from functools import wraps
from typing import Any, Callable, TypeVar

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])


class Asset:
    def __init__(self, fn: WrappedFn) -> None:
        self.fn = fn

    def __call__(self) -> Any:
        return self.fn()


def asset(fn: WrappedFn) -> Asset:
    @wraps(fn)
    def asset_wrapper() -> Asset:
        return Asset(fn)

    return asset_wrapper()
