from __future__ import annotations

import inspect
from typing import Any, Callable, Optional, Type, Union

from optool.fields.util import check_only_one_specified, get_type_validator


class CallableParameterError(ValueError):

    def __init__(self, *, spec: str, expected: Any, value: inspect.FullArgSpec) -> None:
        super().__init__(f"expected the {spec} {expected}, but got a value with argument specification {value}")


class UnverifiableCallableParameterError(ValueError):

    def __init__(self, *, spec: str, expected: Any, value: inspect.FullArgSpec) -> None:
        super().__init__(f"cannot verify the callable with argument specification {value} "
                         f"for expected {spec} {expected}")


class ConstrainedCallable:
    """
    Pydantic-compatible field type for :py:class:`typing.Callable` objects.

    See Also:
        `Pydantic documentation: Custom Data Types <https://docs.pydantic.dev/usage/types/#custom-data-types>`_ and
        class :py:class:`pydantic.types.ConstrainedInt` or similar of :py:mod:`pydantic`
    """

    num_params: Optional[int] = None
    param_types: Optional[tuple[type, ...]]
    return_type: Optional[type] = None

    @classmethod
    def __get_validators__(cls):
        yield get_type_validator(Callable)
        yield cls.validate_number_of_parameters
        yield cls.validate_parameter_types
        yield cls.validate_return_type

    @classmethod
    def validate_number_of_parameters(cls, val: Callable) -> Callable:
        if cls.num_params is None:
            return val

        arg_spec = cls._check_can_verify_params("number of parameters", cls.num_params, val)
        if len(arg_spec.args) == cls.num_params:
            return val
        raise CallableParameterError(spec="number of parameters", expected=cls.num_params, value=arg_spec)

    @classmethod
    def validate_parameter_types(cls, val: Callable) -> Callable:
        if cls.param_types is None:
            return val

        arg_spec = cls._check_can_verify_params("parameter types", cls.num_params, val)
        if not arg_spec.annotations:
            raise CallableParameterError(spec="parameter types", expected=cls.num_params, value=arg_spec)
        if cls.param_types == tuple(arg_spec.annotations[name] for name in arg_spec.args):
            return val
        raise CallableParameterError(spec="parameter types", expected=cls.param_types, value=arg_spec)

    @classmethod
    def validate_return_type(cls, val: Callable) -> Callable:
        if cls.return_type is None:
            return val

        arg_spec: inspect.FullArgSpec = inspect.getfullargspec(val)
        if 'return' not in arg_spec.annotations:
            raise UnverifiableCallableParameterError(spec="return type", expected=cls.num_params, value=arg_spec)
        if cls.return_type == arg_spec.annotations['return']:
            return val
        raise UnverifiableCallableParameterError(spec="return type", expected=cls.return_type, value=arg_spec)

    @classmethod
    def _check_can_verify_params(cls, spec: str, expected: Optional[int], val: Callable) -> inspect.FullArgSpec:
        arg_spec = inspect.getfullargspec(val)
        if arg_spec.varargs or arg_spec.varkw:
            raise UnverifiableCallableParameterError(spec=spec, expected=expected, value=arg_spec)
        return arg_spec


def concallable(*,
                num_params: Optional[int] = None,
                param_types: Union[type, tuple[type, ...], None] = None,
                return_type: Optional[type] = None) -> Type[Callable]:
    check_only_one_specified(num_params, param_types, "Cannot specify both number and types of parameters.")
    if isinstance(param_types, type):
        param_types = (param_types,)
    namespace = dict(num_params=num_params, param_types=param_types, return_type=return_type)
    return type('ConstrainedCallableValue', (ConstrainedCallable,), namespace)
