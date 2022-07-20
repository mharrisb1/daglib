from typing import Any, Iterable, TypeVar, Callable

from daglib.profiling import profiling_wrapper

WrappedFn = TypeVar("WrappedFn", bound=Callable[..., Any])


class Task:
    def __init__(
        self,
        dag_name: str,
        dag_description: str,
        run_id: str,
        profile: bool,
        profile_dir: str,
        fn: WrappedFn,
        inputs: Any | Iterable[Any] = (),
        suffix: str | None = None,
        name_override: str | None = None,
    ) -> None:
        name = name_override if name_override else fn.__name__
        self.name = name if not suffix else f"{name} {suffix}"
        self.description = fn.__doc__ or ""

        if inputs == () and fn.__code__.co_argcount > 0:
            self.inputs = fn.__code__.co_varnames[: fn.__code__.co_argcount]
        elif not isinstance(inputs, Iterable) or isinstance(inputs, str):
            self.inputs = tuple([inputs])
        else:
            self.inputs = tuple(inputs)
        if not profile:
            self.fn = fn
        if profile:
            self.fn = profiling_wrapper(
                dag_name, dag_description, run_id, self.name, self.description, profile_dir, fn, *inputs
            )
