from dataclasses import dataclass
from decimal import Decimal

__all__ = [
    "FinitePoset",
    "Numbers",
    "Poset",
    "PosetProduct",
]


@dataclass
class Poset:
    """The base class for Posets"""


@dataclass
class Numbers(Poset):
    """

    This represents a closed interval of numbers.

    The top and bottom are given as decimals. Top might be +inf.

    The units are given as a string. If empty, the units are dimensionless.

    The **step** is given as a decimal. If 0, the poset is "continuous", in the
    sense that all decimals are allowed. If non-zero, then it represents the steps.
    For example, the natural numbers are given by bottom=0, top=+inf, step=1.

    The numbers [0, 0.5, 1.0, 1.5, 2.0] are given by bottom=0.5, top=2.0, step=0.1.


    Attributes:
        bottom (Decimal): Lower bound of the interval.
        top (Decimal): Upper bound of the interval.
        step (Decimal): Step of the interval. If 0, the poset is "continuous".
        units (str): Units of the interval. If an empty string, the units are dimensionless.

    """

    bottom: Decimal
    top: Decimal
    step: Decimal  # if 0 = "continuous"
    units: str  # if empty = dimensionless


@dataclass
class FinitePoset(Poset):
    """
    Represents a finite poset of elements

    Attributes:
        elements: A set of strings
        relations: A set of pairs of strings that represent the relations between the elements


    Examples:

        >>> FinitePoset(elements={'a', 'b', 'c'}, relations={('a', 'b'), ('b', 'c')})

    """

    elements: set[str]
    relations: set[tuple[str, str]]


@dataclass
class PosetProduct(Poset):
    """
    Represents the product of 0 or more posets.
    Its elements are tuples of elements of the posets.

    """

    subs: list[Poset]
