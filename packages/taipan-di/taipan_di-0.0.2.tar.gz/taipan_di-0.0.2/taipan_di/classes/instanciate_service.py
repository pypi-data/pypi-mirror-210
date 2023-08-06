import sys
from abc import ABC
from inspect import Parameter as InspectParameter, signature
from typing import (
    Any,
    Callable,
    Dict,
    NewType,
    Tuple,
    Type,
    TypeVar,
    Union,
    ForwardRef,
    cast,
)
from typing_extensions import Protocol

from taipan_di.interfaces import BaseDependencyProvider
from taipan_di.errors import TaipanInjectionError


S = TypeVar("S")

ServiceDefinition = Type[S]
ServiceResult = S

Undefined = NewType("Undefined", int)


class _ProtocolInit(Protocol):
    pass


_no_init = _ProtocolInit.__init__


def _resolve_forward_reference(module: Any, ref: Union[str, ForwardRef]) -> Any:
    if isinstance(ref, str):
        name = ref
    else:
        name = ref.__forward_arg__

    if name in sys.modules[module].__dict__:
        return sys.modules[module].__dict__[name]

    return None


class Parameter:
    type: Any
    name: str
    default: Any

    def __init__(self, name: str, type: Any = Any, default: Any = Undefined):
        self.name = name
        self.type = type
        self.default = default


def _inspect_function_arguments(
    function: Callable,
) -> Dict[str, Parameter]:
    parameters = {}

    for name, parameter in signature(function).parameters.items():
        if isinstance(parameter.annotation, (str, ForwardRef)) and hasattr(
            function, "__module__"
        ):
            annotation = _resolve_forward_reference(
                function.__module__, parameter.annotation
            )
        else:
            annotation = parameter.annotation

        parameters[name] = Parameter(
            parameter.name,
            annotation,
            parameter.default
            if parameter.default is not InspectParameter.empty
            else Undefined,
        )

    return parameters


def _resolve_function_kwargs(
    parameters_name: Tuple[str, ...],
    parameters: Dict[str, Parameter],
    provider: BaseDependencyProvider,
) -> Dict[str, Any]:
    resolved_kwargs = {}

    for name in parameters_name:
        if provider.contains(parameters[name].type):
            resolved_kwargs[name] = provider.resolve(parameters[name].type)
            continue

        if parameters[name].default is not Undefined:
            resolved_kwargs[name] = parameters[name].default

    return resolved_kwargs


def instanciate_service(service: Type[S], provider: BaseDependencyProvider) -> S:
    constructor = getattr(service, "__init__")

    # ignore abstract class initialiser and protocol initialisers
    if (
        constructor in [ABC.__init__, _no_init] or constructor.__name__ == "_no_init"
    ):  # FIXME: fix this when typing_extensions library gets fixed
        return constructor

    # Add class definition to dependency injection
    parameters = _inspect_function_arguments(constructor)
    parameters_name = tuple([p for p in parameters.keys() if p != "self"])

    def _resolve_kwargs() -> dict:
        if len(parameters_name) == 0:
            return {}

        resolved_kwargs = _resolve_function_kwargs(parameters_name, parameters, provider)

        if len(resolved_kwargs) < len(parameters_name):
            missing_parameters = [
                arg for arg in parameters_name if arg not in resolved_kwargs
            ]
            raise TaipanInjectionError(
                "Cannot execute function without required parameters. "
                + f"Did you forget to bind the following parameters: `{'`, `'.join(missing_parameters)}`?"
            )

        return resolved_kwargs

    all_kwargs = _resolve_kwargs()
    instance = service(**all_kwargs)

    result = cast(S, instance)
    return result
