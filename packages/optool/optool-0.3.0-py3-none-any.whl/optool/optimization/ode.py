from abc import ABC, abstractmethod
from enum import auto
from typing import Any, Dict, final

from casadi import casadi
from pandas import DatetimeIndex
from pydantic import root_validator

from optool import BaseModel, validate_arguments
from optool.conversions import datetime_index_to_intervals
from optool.fields.callables import concallable
from optool.fields.misc import NonEmptyStr
from optool.fields.quantities import QuantityLike
from optool.fields.symbolic import CasadiColumn
from optool.fields.util import validate
from optool.logging import LOGGER
from optool.math import num_elements
from optool.uom import UNITS, Quantity
from optool.util import StrEnum


class OrdinaryDifferentialEquation(BaseModel, frozen=True):
    r"""
    Representation of an ordinary differential equation (ODE).

    An ODE is described by the mathematical formula of the following form,

    .. math::
        \dot{x} = f(x, u),

    where :math:`x` represents the state variable and :math:`u` the input variable that includes both controlled signals
    and disturbances.

    The corresponding implementation requires the definition of the state variable, the input variable, and the function
    :math:`f`. The transcription then follows a multiple shooting approach, where the continuity is ensured via
    so-called gap closing constraints. In order to use the associated vector-based formulation, both :math:`x` and
    :math:`u` should be specified as column vectors, where :math:`u` has one element less than :math:`x`.
    """

    name: NonEmptyStr
    """The name of the ordinary differential equation."""
    state_variable: QuantityLike[Any, CasadiColumn]
    """The array of state variables of the ordinary differential equation."""
    input_variable: QuantityLike[Any, CasadiColumn]
    """The array of input variables of the ordinary differential equation."""
    function: concallable(num_params=2)  # type: ignore[valid-type]
    """The function of the ordinary differential equation."""

    @final
    @root_validator
    def _is_consistent(cls, values: Dict) -> Dict:
        name = values['name']
        function = values['function']
        state_variable = values['state_variable']
        input_variable = values['input_variable']
        num_state_variables = num_elements(state_variable)
        num_input_variables = num_elements(input_variable)

        if num_state_variables != num_input_variables + 1:
            raise ValueError(f"The vector of state variables for the ODE function {name} must have one element more "
                             f"than the vector of input variables, but have {num_state_variables=} and "
                             f"{num_input_variables=}.")

        try:
            time_derivative = function(state_variable[1:], input_variable)
        except Exception as e:
            raise ValueError(f"The given ODE function {name} failed with given state and input variables.") from e
        else:
            validate(time_derivative, [lambda x: isinstance(x, Quantity), lambda x: isinstance(x.magnitude, casadi.SX)],
                     "Result of the ODE, i.e., time-derivative")

            validate(
                time_derivative, lambda x: x.units.is_compatible_with(state_variable.units / UNITS.second),
                f"The time-derivative for the ODE function {name} has units {time_derivative.units}, which "
                f"is not compatible with the units of the state variables, i.e., '{state_variable.units}'.")

            validate(
                time_derivative, lambda x: x.size() == (num_input_variables, 1),
                f"The vector of time-derivatives for the ODE function {name} must have the same number of "
                f"elements than the vector of input variables, but have {time_derivative.numel()} and "
                f"{num_input_variables}.")

        return values


class Equation(BaseModel, frozen=True):
    """
    Representation of a formula that expresses the equality of two expressions, by connecting them with the equals sign.
    """

    lhs: QuantityLike[Any, CasadiColumn]
    """The left-hand side of the equation."""
    rhs: QuantityLike[Any, CasadiColumn]
    """The right-hand side of the equation."""


class BaseIntegrationMethod(ABC):

    @classmethod
    @abstractmethod
    def integrate(cls, ode: OrdinaryDifferentialEquation, timestamps: DatetimeIndex) -> Equation:
        raise NotImplementedError()


class ForwardEuler(BaseIntegrationMethod):
    r"""
    The Euler method for numerical integration.

    The forward Euler method, also simply referred to as the Euler method, is the most basic explicit method for
    numerical integration of ODEs and is the simplest Runge–Kutta method.

    One step of the Euler method from :math:`i` to :math:`i+1` is given by

    .. math::
        x[i+1] = x[i] + T_s[i] \cdot f \left( x[i], u[i] \right),

    where :math:`T_s[i]` is the time between index :math:`i` and :math:`i+1`.

    See Also:
        `Wikipedia: Euler method <https://en.wikipedia.org/wiki/Euler_method>`_
    """

    @classmethod
    def integrate(cls, ode: OrdinaryDifferentialEquation, timestamps: DatetimeIndex) -> Equation:
        LOGGER.debug("Integrating {} with {}.", ode.name, cls.__name__)

        time_intervals = datetime_index_to_intervals(timestamps)
        time_derivative = ode.function(ode.state_variable[1:], ode.input_variable)
        return Equation(lhs=ode.state_variable[1:], rhs=ode.state_variable[:-1] + time_intervals * time_derivative)


class RungeKutta4(BaseIntegrationMethod):
    r"""
    Fourth-order method of the Runge–Kutta for numerical integration.

    Runge-Kutta 4 is the fourth-order method of the Runge–Kutta family, which is the most widely used Runge-Kutta method
    and thus also referred to as the classic Runge–Kutta method or simply the Runge–Kutta method.

    One step of the Runge-Kutta method from :math:`i` to :math:`i + 1` is given by

    .. math::
        x[i+1] = x[i] + \frac{1}{6}\, T_s[i] \big( k_1 + 2k_2 + 2k_3 + k_4 \big),

    where the parameters :math:`k_1, \ldots, k_4` are recursively defined as follows:

    .. math::
        k_1 &= f \big( x[i], u[i] \big), \\
        k_2 &= f \big( x[i] + k_1 \tfrac{T_s[i]}{2}, u[i] \big), \\
        k_3 &= f \big( x[i] + k_2 \tfrac{T_s[i]}{2}, u[i] \big), \\
        k_4 &= f \big( x[i] + k_3 T_s[i], u[i] \big).

    Note that, if the time-derivative of :math:`x` is not dependent on :math:`x` itself, i.e., :math:`f(x,u) = f(u)`,
    all parameters above are equal, i.e., :math:`k_1 = k_2 = k_3 = k_4`. Hence, the Runge-Kutta method is equal to the
    Euler method.

    See Also:
        `Wikipedia: Runge–Kutta methods <https://en.wikipedia.org/wiki/Runge–Kutta_methods>`_
    """

    @classmethod
    def integrate(cls, ode: OrdinaryDifferentialEquation, timestamps: DatetimeIndex) -> Equation:
        LOGGER.debug("Integrating {} with {}.", ode.name, cls.__name__)

        time_intervals = datetime_index_to_intervals(timestamps)
        k1 = ode.function(ode.state_variable[1:], ode.input_variable)
        k2 = ode.function(ode.state_variable[1:] + time_intervals / 2 * k1, ode.input_variable)
        k3 = ode.function(ode.state_variable[1:] + time_intervals / 2 * k2, ode.input_variable)
        k4 = ode.function(ode.state_variable[1:] + time_intervals * k3, ode.input_variable)
        next_state = ode.state_variable[1:] + time_intervals / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

        return Equation(lhs=ode.state_variable[1:], rhs=next_state)


class IntegrationMethod(StrEnum):
    FORWARD_EULER = auto()
    RUNGE_KUTTA_4 = auto()

    @classmethod
    @validate_arguments
    def integrate(cls, ode: OrdinaryDifferentialEquation, timestamps: DatetimeIndex) -> Equation:
        if cls.FORWARD_EULER:
            return ForwardEuler.integrate(ode, timestamps)
        if cls.RUNGE_KUTTA_4:
            return RungeKutta4.integrate(ode, timestamps)
        raise NotImplementedError(f"Missing case for {cls.value}.")
