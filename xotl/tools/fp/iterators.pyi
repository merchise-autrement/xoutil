from typing import Callable, Iterable, TypeVar, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
@overload
def kleisli_compose(
    g: Callable[[B], Iterable[C]], f: Callable[[A], Iterable[B]]
) -> Callable[[A], Iterable[C]]: ...
@overload
def kleisli_compose(*fs: Callable[[A], Iterable[A]]) -> Callable[[A], Iterable[A]]: ...
@overload
def iter_compose(
    g: Callable[[B], Iterable[C]], f: Callable[[A], Iterable[B]]
) -> Callable[[A], Iterable[C]]: ...
@overload
def iter_compose(*fs: Callable[[A], Iterable[A]]) -> Callable[[A], Iterable[A]]: ...
