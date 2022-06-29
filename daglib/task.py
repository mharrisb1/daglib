import os
import time
from functools import partial
from typing import Any, Callable, Iterable

from rich.console import Console

running_with_cli = bool(os.getenv("DL_RUN_WITH_CLI"))


def base_proxy(fn: Callable[..., Any], name: str, *args: Any, **kwargs: Any) -> Any:
    if running_with_cli:
        console = Console()
        with console.status(f"Running task {name}..."):
            t1 = time.time()
            result = fn(*args, **kwargs)
            t2 = time.time()
            timeit = round(t2 - t1, 4)
            console.print(f"{name} complete in {timeit} seconds")
        return result
    else:
        return fn(*args, **kwargs)


class Task:
    def __init__(
        self,
        fn: Callable[..., Any],
        inputs: Any | Iterable[Any] = (),
        suffix: str | None = None,
        name_override: str | None = None,
    ) -> None:
        name = name_override if name_override else fn.__name__
        self.name = name if not suffix else f"{name} {suffix}"

        if inputs == () and fn.__code__.co_argcount > 0:
            self.inputs = fn.__code__.co_varnames[: fn.__code__.co_argcount]
        elif not isinstance(inputs, Iterable) or isinstance(inputs, str):
            self.inputs = tuple([inputs])
        else:
            self.inputs = tuple(inputs)

        self.fn = partial(base_proxy, fn, self.name)
