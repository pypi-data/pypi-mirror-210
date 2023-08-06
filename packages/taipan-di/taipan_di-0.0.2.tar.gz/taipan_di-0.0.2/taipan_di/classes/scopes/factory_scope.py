from typing import Any, Callable, Type, TypeVar, cast
from typeguard import check_type

from taipan_di.interfaces import BaseDependencyProvider, BaseScope
from taipan_di.errors import TaipanTypeError

T = TypeVar("T")

class FactoryScope(BaseScope):
    def __init__(self, creator: Callable[[BaseDependencyProvider], Any]) -> None:
        self._creator = creator

    def get_instance(self, type: Type[T], container: BaseDependencyProvider) -> T:
        instance = self._creator(container)
        
        try:
            result = check_type(instance, type)
            return result
        except:
            raise TaipanTypeError(f"Created instance is not of type {str(type)}")
