from datetime import timedelta
from typing import TYPE_CHECKING, Any, Dict

import pandas as pd
from pydantic import Field, StrictBool, StrictFloat, StrictStr

from optool import BaseModel, orthography
from optool.fields.containers import ConstrainedMutatingList
from optool.fields.misc import NonEmptyStr
from optool.fields.quantities import QuantityLike
from optool.util import ValueRange

if TYPE_CHECKING:
    ValueRangeList = list
else:

    class ValueRangeList(ConstrainedMutatingList[ValueRange]):
        pass


class DebugInfo(BaseModel):
    """
    Container for debug information related to the solving of an optimization problem.
    """

    problem_name: NonEmptyStr = Field(allow_mutation=False)
    """The name of the optimization problem."""

    normed_variable_values: ValueRangeList = []
    normed_constraints_lagrange_multipliers: ValueRangeList = []

    def print_details(self) -> None:
        for val in self.get_details():
            print(val)

    def get_details(self) -> list[str]:
        prefix = "|   "
        separator = f"{prefix}{'-' * 60}"
        details = [
            f"Debug information for the optimization problem entitled '{self.problem_name}'",
            f"{prefix}Normed values of the decision variables (as seen by the solver):", separator
        ]

        self._append_normed_values(details, prefix, self.normed_variable_values)
        details.extend((separator, f"{prefix}Normed values of the lagrange multipliers of the constraints "
                        f"(as seen by the solver):"))

        self._append_normed_values(details, prefix, self.normed_constraints_lagrange_multipliers)
        details.append(separator)
        return details

    @staticmethod
    def _append_normed_values(details: list[str], prefix: str, normed_values: list[ValueRange]) -> None:
        attributes_to_show = ["min", "avg", "max", "max_abs"]
        df = pd.DataFrame(index=attributes_to_show)
        for val in normed_values:
            df[f"{val.name}:  "] = [getattr(val, attr) for attr in attributes_to_show]
        table_rows = df.transpose().to_string().split("\n")
        details.extend(f"{prefix}{row}" for row in table_rows)


class UnsuccessfulOptimization(Exception):
    """
    Unsuccessful attempt to solve the optimization problem.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SolverResponse(BaseModel, frozen=True):
    """
    The response returned by the solver.
    """

    problem_name: StrictStr
    """The name of the optimization problem."""

    function_value: QuantityLike[Any, StrictFloat]
    success: StrictBool
    solver_status: Dict[str, Any]
    debug_info: DebugInfo

    def get_return_status(self) -> str:
        return self.solver_status["return_status"]

    def get_number_of_iterations(self) -> int:
        return int(self.solver_status["iter_count"])

    def get_solver_time(self) -> timedelta:
        # See https://groups.google.com/g/casadi-users/c/dMSGV8KII30?pli=1 for an explanation of both
        # 't_wall_total' and 't_proc_total' and the difference between them.
        return timedelta(seconds=self.solver_status["t_wall_total"])

    def guarantee_success(self):
        if not self.success:
            raise UnsuccessfulOptimization(f"The problem entitled '{self.problem_name}' was not solved successfully, "
                                           f"but returned with '{self.get_return_status()}'.")

    def get_message(self):
        success_msg = "" if self.success else "NOT "
        duration_str = orthography.naturaldelta(self.get_solver_time(), minimum_unit="microseconds")
        return f"The optimization problem {self.problem_name!r} was {success_msg}solved successfully " \
               f"after {self.get_number_of_iterations()} iterations and {duration_str} " \
               f"with return status {self.get_return_status()!r}."


class IpoptOption(BaseModel, frozen=True):
    """
    The options available in Ipopt.

    See Also:
        `Ipopt documentation <https://coin-or.github.io/Ipopt/OPTIONS.html#OPT_print_options_documentation>`_
    """

    category: NonEmptyStr
    """The category of the option."""

    name: NonEmptyStr
    """The name of the option."""

    values: NonEmptyStr
    """The possible values to set."""

    description: NonEmptyStr
    """The description of the option."""

    def pretty_print(self):
        print(f"{self.name}: ({self.category})\t{self.values}:\n{self.description}")
