from __future__ import annotations

from typing import Callable, TypeVar, cast

from typing_extensions import ParamSpec

R = TypeVar("R")
P = ParamSpec("P")


def initialized(func: Callable[P, R]) -> Callable[P, R]:
    """This decorator checks that the class has been initialized before calling the
    decorated method.

    Args:
        func: The function to decorate.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = cast(Initiable, args[0])
        if not self.initialized:
            raise RuntimeError(
                f"The class `{self.__class__.__name__}` has not been initialized. Call"
                " its `init` method first."
            )
        return func(*args, **kwargs)

    return wrapper


class Initiable:
    """Base class for components that need to be initialized before being used.

    Attributes:
        initialized: Whether the class has been initialized.
    """

    def __init__(self) -> None:
        self.initialized = False

    def init(self) -> None:
        """Init the class downloading, loading a model, connecting to an external
        service, etc."""
        self.initialized = True
