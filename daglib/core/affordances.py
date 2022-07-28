from typing import Any

from daglib.core.types import WrappedFn, FnInput


class FnCallProxying:
    def __init__(self, fn: WrappedFn) -> None:
        self.fn = fn

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


class FnDeconstructing:
    def __init__(self, fn: WrappedFn) -> None:
        self.fn = fn

    @property
    def name(self) -> str:
        """
        Get name of function

        :return: Name
        """
        return self.fn.__name__

    @property
    def doc(self) -> str | None:
        """
        Get docstring for function

        :return: Docstring or None
        """
        return self.fn.__doc__

    @property
    def annotations(self) -> dict[str, type]:
        """
        Get function annotations
        https://peps.python.org/pep-3107/#:~:text=Function%20annotations%2C%20both%20for%20parameters,meaning%20or%20significance%20to%20annotations.

        :return: Function annotations
        """
        return self.fn.__annotations__

    @property
    def is_annotated(self) -> bool:
        """
        Show whether the function is annotated

        :return: True if annotated else False
        """
        return bool(self.annotations)

    @property
    def return_type(self) -> type | None:
        """
        Get return type of function if specified. Else None

        :return: Return type or None
        """
        return self.annotations.get("return", None)

    @property
    def defaults(self) -> tuple[Any, ...]:
        """
        Get default values set in function arguments

        :return: Tuple of default values
        """
        return tuple(reversed(self.fn.__defaults__)) if self.fn.__defaults__ else tuple()  # type: ignore

    @property
    def has_defaults(self) -> bool:
        """
        Show whether the function has defaults

        :return: True if it has defaults else False
        """
        return bool(self.defaults)

    @property
    def inputs(self) -> list[FnInput]:
        """
        Get function inputs of function

        :return: Object containing function name, type [optional], default [optional]
        """
        inputs = [FnInput(n, None, None) for n in self.fn.__code__.co_varnames[: self.fn.__code__.co_argcount]]

        # Add types if any
        for n in range(len(inputs)):
            inputs[n].type = self.annotations.get(inputs[n].name)

        # Add defaults if any
        if self.has_defaults:
            for i, d in enumerate(self.defaults):
                inputs[len(inputs) - 1 - i].default = d

        return inputs

    @property
    def has_inputs(self) -> bool:
        """
        Show whether the function has inputs

        :return: True if it has inputs else False
        """
        return bool(self.inputs)
