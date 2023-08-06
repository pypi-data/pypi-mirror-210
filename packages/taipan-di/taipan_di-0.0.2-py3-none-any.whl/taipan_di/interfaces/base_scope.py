import abc
from typing import Type, TypeVar

from .base_dependency_provider import BaseDependencyProvider

T = TypeVar("T")


class BaseScope(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "get_instance")
            and callable(subclass.get_instance)
            or NotImplemented
        )

    @abc.abstractmethod
    def get_instance(self, type: Type[T], container: BaseDependencyProvider) -> T:
        raise NotImplementedError()
