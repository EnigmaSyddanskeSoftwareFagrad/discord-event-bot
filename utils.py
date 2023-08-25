from typing import Callable, Iterable, TypeVar

T = TypeVar('T')


def find(collection: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    for element in collection:
        if predicate(element):
            return element
