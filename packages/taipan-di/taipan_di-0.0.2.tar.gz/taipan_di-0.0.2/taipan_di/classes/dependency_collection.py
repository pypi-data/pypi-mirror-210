from typing import Any, Callable, Type, TypeVar

from taipan_di.interfaces import BaseDependencyProvider
from taipan_di.errors import TaipanTypeError
from typeguard import check_type

from .dependency_container import DependencyContainer
from .instanciate_service import instanciate_service
from .scopes import FactoryScope, SingletonScope


T = TypeVar("T")
U = TypeVar("U")


class DependencyCollection:
    def __init__(self) -> None:
        self._container = DependencyContainer()

    # Public methods

    def register_singleton_creator(
        self, type: Type[T], creator: Callable[[BaseDependencyProvider], T]
    ) -> None:
        service = SingletonScope(creator)
        self._container.register(type, service)

    def register_singleton_instance(self, type: Type[T], instance: T) -> None:
        self._assert_instance_type(instance, type)

        creator = lambda provider: instance
        self.register_singleton_creator(type, creator)

    def register_singleton(
        self, interface_type: Type[T], implementation_type: Type[U] = None
    ) -> None:
        if implementation_type is None:
            implementation_type = interface_type
            
        self._assert_implementation_derives_interface(implementation_type, interface_type)

        creator = lambda provider: instanciate_service(implementation_type, provider)
        self.register_singleton_creator(interface_type, creator)

    def register_factory_creator(
        self, type: Type[T], creator: Callable[[BaseDependencyProvider], T]
    ) -> None:
        service = FactoryScope(creator)
        self._container.register(type, service)

    def register_factory(
        self, interface_type: Type[T], implementation_type: Type[U] = None
    ) -> None:
        if implementation_type is None:
            implementation_type = interface_type
            
        self._assert_implementation_derives_interface(implementation_type, interface_type)

        creator = lambda provider: instanciate_service(implementation_type, provider)
        self.register_factory_creator(interface_type, creator)

    def build(self) -> BaseDependencyProvider:
        return self._container.build()

    # Private methods

    def _assert_instance_type(self, instance: Any, type: Type) -> None:
        try:
            check_type(instance, type)
        except:
            raise TaipanTypeError(f"Provided instance is not of type {str(type)}")

    def _assert_implementation_derives_interface(
        self, implementation_type: Type[U], interface_type: Type[T]
    ) -> None:
        if not issubclass(implementation_type, interface_type):
            raise TaipanTypeError(
                "Implementation type %s must derive from interface type %s",
                str(implementation_type),
                str(interface_type),
            )
