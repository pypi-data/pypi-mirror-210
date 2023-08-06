from typing import Any, Callable, Type, TypeVar, cast

from taipan_di.interfaces import BaseDependencyProvider, BaseScope
from taipan_di.errors import TaipanTypeError

T = TypeVar("T")

class FactoryScope(BaseScope):
    def __init__(self, creator: Callable[[BaseDependencyProvider], Any]) -> None:
        self._creator = creator

    def get_instance(self, type: Type[T], container: BaseDependencyProvider) -> T:
        instance = self._creator(container)

        if not isinstance(instance, type):
            raise TaipanTypeError("Created instance is not of type %s", str(type))

        result = cast(T, instance)
        return result
