from typing import Dict, Type, TypeVar

from taipan_di.errors import TaipanUnregisteredError
from taipan_di.interfaces import BaseDependencyProvider, BaseScope

T = TypeVar("T")


class DependencyProvider(BaseDependencyProvider):
    def __init__(self, services: Dict[Type, BaseScope]) -> None:
        self._services = services.copy()

    def contains(self, type: Type[T]) -> bool:
        return type in self._services

    def resolve(self, type: Type[T]) -> T:
        if not type in self._services:
            raise TaipanUnregisteredError("Service %s is not registered", str(type))

        service = self._services[type]
        result = service.get_instance(type, self)

        return result
