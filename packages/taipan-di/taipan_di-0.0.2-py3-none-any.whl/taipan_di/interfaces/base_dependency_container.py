import abc
from typing import Type, TypeVar

from .base_dependency_provider import BaseDependencyProvider
from .base_scope import BaseScope

T = TypeVar("T")

class BaseDependencyContainer(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "contains")
            and callable(subclass.contains)
            and hasattr(subclass, "register")
            and callable(subclass.register)
            and hasattr(subclass, "build")
            and callable(subclass.build)
            or NotImplemented
        )

    @abc.abstractmethod    
    def contains(self, type: Type[T]) -> bool:
        raise NotImplementedError

    @abc.abstractmethod    
    def register(self, type: Type, service: BaseScope) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod    
    def build(self) -> BaseDependencyProvider:
        raise NotImplementedError