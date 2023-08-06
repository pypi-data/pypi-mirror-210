from typing import TYPE_CHECKING

from pydantic import ConstrainedFloat, ConstrainedStr

if TYPE_CHECKING:
    NonEmptyStr = str

    FractionFloat = float
    PositiveFiniteFloat = float
    NonNegativeFiniteFloat = float

else:

    class NonEmptyStr(ConstrainedStr):
        strict = True
        strip_whitespace = True
        min_length = 1

    class FractionFloat(ConstrainedFloat):
        """
        A number that needs to be greater or equal to zero and smaller or equal to one.
        """
        strict = False
        ge = 0.0
        le = 1.0
        allow_inf_nan = False

    class PositiveFiniteFloat(ConstrainedFloat):
        strict = False
        gt = 0
        allow_inf_nan = False

    class NonNegativeFiniteFloat(ConstrainedFloat):
        strict = False
        ge = 0
        allow_inf_nan = False
