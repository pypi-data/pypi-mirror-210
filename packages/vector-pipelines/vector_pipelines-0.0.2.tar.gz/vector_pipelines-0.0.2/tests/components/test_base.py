from __future__ import annotations

from contextlib import ExitStack as does_not_raise

import pytest

from vector_pipelines.components.init import Initiable, initialized


class Dummy(Initiable):
    @initialized
    def dummy_method(self) -> None:
        pass


def test_initiable() -> None:
    """Test that the `init` method sets the `initialized` attribute to `True`."""
    initiable = Initiable()
    assert not initiable.initialized

    initiable.init()
    assert initiable.initialized


def test_initialized() -> None:
    """Test that the decorated method does not raise any exception if the class method
    `init` has been called."""
    dummy = Dummy()
    dummy.init()

    with does_not_raise():
        dummy.dummy_method()


def test_initialized_raise_runtime_error() -> None:
    """Test that the decorated method raises a `RuntimeError` if the class method `init`
    has not been called."""
    dummy = Dummy()

    with pytest.raises(RuntimeError):
        dummy.dummy_method()
