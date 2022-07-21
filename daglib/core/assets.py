from functools import wraps
from typing import Any, Callable, TypeVar

from daglib.core.task import Task

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])


def asset(fn: WrappedFn) -> Task:
    @wraps(fn)
    def simple_task() -> Task:
        return Task("", "", "", False, "", fn)

    return simple_task()
