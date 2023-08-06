import abc
from typing import Type, TypeVar

T = TypeVar("T")


class BaseDependencyProvider(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "contains")
            and callable(subclass.contains)
            and hasattr(subclass, "resolve")
            and callable(subclass.resolve)
            or NotImplemented
        )

    @abc.abstractmethod
    def contains(self, type: Type[T]) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def resolve(self, type: Type[T]) -> T:
        raise NotImplementedError
