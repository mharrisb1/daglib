from typing import Any, Iterable, TypeVar, Callable

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])


class Task:
    def __init__(
        self,
        fn: WrappedFn,
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
        self.fn = fn
