from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from .posets import Poset

__all__ = [
    "AmbientConversion",
    "CatalogueDP",
    "Constant",
    "DPLoop2",
    "DPSeries",
    "EntryInfo",
    "IdentityDP",
    "JoinNDP",
    "Limit",
    "M_Ceil_DP",
    "M_FloorFun_DP",
    "M_Fun_AddConstant_DP",
    "M_Fun_AddMany_DP",
    "M_Fun_MultiplyConstant_DP",
    "M_Fun_MultiplyMany_DP",
    "M_Fun_MultiplyMany_DP",
    "M_Power_DP",
    "M_Res_AddConstant_DP",
    "M_Res_AddMany_DP",
    "M_Res_DivideConstant_DP",
    "M_Res_MultiplyConstant_DP",
    "M_Res_MultiplyMany_DP",
    "MeetNDualDP",
    "MeetNDualDP",
    "Mux",
    "ParallelDP",
    "PrimitiveDP",
    "UnitConversion",
    "ValueFromPoset",
]


@dataclass
class PrimitiveDP:
    r"""
    A generic PrimitiveDP; a morphism of the category DP.

    Other classes derive from this.

    Attributes:
        description: An optional string description.
        F: The functionality poset $\F$
        R: The resources poset $\R$
    """

    description: Optional[str]
    F: Poset
    R: Poset


@dataclass
class DPSeries(PrimitiveDP):
    r"""
    A series composition of two or more DPs.

    Attributes:
        F: The functionality poset $\F$
        R: The resources poset $\R$
        subs: The list of DPs
    """

    subs: list[PrimitiveDP]


@dataclass
class ParallelDP(PrimitiveDP):
    r""" """

    subs: list[PrimitiveDP]


@dataclass
class ValueFromPoset:
    r"""
    A value in a particular poset (a "typed" value).

    Depending on the poset, we have different types:

    - For [FinitePoset][act4e_mcdp.posets.FinitePoset] the values are strings.
    - For [Numbers][act4e_mcdp.posets.Numbers] the values are instances of Decimal.
    - For [PosetProduct][act4e_mcdp.posets.PosetProduct] the values are tuples of values.


    Attributes:
        value (str | Decimal | tuple): The value $x \in \posA$
        poset: The poset $\posA$

    """

    value: object
    poset: Poset


@dataclass
class M_Res_MultiplyConstant_DP(PrimitiveDP):
    r"""
    Multiplication by a constant on the left side.

    Relation:

        $$
            \fun \cdot_{\opspace} v \leq_{\opspace} \res
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        vu: The value $v$ to be added.
        opspace: The poset $\opspace$ where the multiplication and comparison take place.

    """

    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Res_DivideConstant_DP(PrimitiveDP):
    r""" """

    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Fun_MultiplyConstant_DP(PrimitiveDP):
    r"""
    Multiplication by a constant on the right side.

    Relation:

        $$
            \fun \leq_{\opspace} \res  \cdot_{\opspace} v
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        vu: The value $v$ to be added.
        opspace: The poset $\opspace$ where the multiplication and comparison take place.

    """
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Res_AddConstant_DP(PrimitiveDP):
    r"""
    Addition of a constant on the left side.

    Relation:

        $$
            \fun +_{\opspace} v \leq_{\opspace} \res
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        vu: The value $v$ to be added.
        opspace: The poset $\opspace$ where the multiplication and comparison take place.

    """
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Fun_AddMany_DP(PrimitiveDP):
    r"""
    Addition on the right side.

    The resources posets is a PosetProduct of, in general, $n$ elements $\F_1, \F_2, \dots$.
    (You can assume $n = 2$).


    Relation:

        $$
            \fun \leq_{\opspace}  \res_1 +_{\opspace} \res_2 +_{\opspace} \dots
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        opspace: The poset $\opspace$ where the operations and comparisons take place.

    """
    opspace: Poset


@dataclass
class M_Res_AddMany_DP(PrimitiveDP):
    r"""
    Addition on the left side.


    Relation:

        $$
            \fun_1 +_{\opspace} \fun_2 +_{\opspace} \dots \leq_{\opspace}  \res
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        opspace: The poset $\opspace$ where the operations and comparisons take place.

    """
    opspace: Poset


@dataclass
class MeetNDualDP(PrimitiveDP):
    r"""
    This DP is used as plumbing. It is the dual of [JoinNDP][act4e_mcdp.primitivedps.JoinNDP].


    The functionality posets is a PosetProduct of, in general, $n$ elements $\F_1, \F_2, \dots$.

    We ask that the resource is greater than each of the functionalities.

    The comparison is done in a poset $\opspace$ which contains $\R, \F_1, \F_2,  \dots$.

    Relation:

        $$
            (\fun_1 \leq_{\opspace}  \res) \wedge (\fun_2 \leq_{\opspace} \res) \wedge \dots
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        opspace: The poset $\opspace$ where the comparisons take place.


    """
    opspace: Poset


@dataclass
class JoinNDP(PrimitiveDP):
    r"""
    This DP is used as plumbing. It is the dual of [MeetNDualDP][act4e_mcdp.primitivedps.MeetNDualDP].

    The resources posets is a PosetProduct of, in general, $n$ elements $\R_1, \R_2, \dots$.

    We ask that the functionality is less than each of the resources.

    The comparison is done in a poset $\opspace$ which contains $\F, \R_1, \R_2, \dots$.

    Relation:

        $$
            (\fun \leq_{\opspace}  \res_1) \wedge (\fun \leq_{\opspace} \res_2) \wedge \dots
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        opspace: The poset $\opspace$ where the comparisons take place.


    """

    opspace: Poset


@dataclass
class Mux(PrimitiveDP):
    r""" """

    coords: object


@dataclass
class M_Power_DP(PrimitiveDP):
    r""" """
    num: int
    den: int


@dataclass
class M_Fun_MultiplyMany_DP(PrimitiveDP):
    r"""
    Multiplication on the right side.


    Relation:

        $$
            \fun \leq_{\opspace}  \res_1 \cdot_{\opspace} \res_2 \cdot_{\opspace} \dots
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        opspace: The poset $\opspace$ where the operations and comparisons take place.
    """
    opspace: Poset


@dataclass
class M_Res_MultiplyMany_DP(PrimitiveDP):
    r"""
    Multiplication on the left side.


    Relation:

        $$
            \fun_1 \cdot_{\opspace} \fun_2 \cdot_{\opspace} \dots \leq_{\opspace}  \res
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        opspace: The poset $\opspace$ where the operations and comparisons take place.

    """
    opspace: Poset


@dataclass
class M_Ceil_DP(PrimitiveDP):
    r"""

    Relation:

        $$
            \text{ceil}(\fun) ≤_{\opspace} \res
        $$

    Attributes:
       F (Poset): The functionality poset $\F$
       R (Poset): The resources poset $\R$
       opspace: The poset $\opspace$ where the comparisons take place.

    """
    opspace: Poset


@dataclass
class M_FloorFun_DP(PrimitiveDP):
    r"""

    Relation:

        $$
            \fun ≤_{\opspace} \text{floor}(\res)
        $$

    Attributes:
       F (Poset): The functionality poset $\F$
       R (Poset): The resources poset $\R$
       opspace: The poset $\opspace$ where the comparisons take place.

    """

    opspace: Poset


@dataclass
class M_Fun_AddConstant_DP(PrimitiveDP):
    r"""
    Addition of a constant on the right side.

    Relation:

        $$
            \fun \leq_{\opspace} \res +_{\opspace} v
        $$

    Attributes:
        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        vu: The value $v$ to be added.
        opspace: The poset $\opspace$ where the multiplication and comparison take place.

    """
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class UnitConversion(PrimitiveDP):
    r"""

    A unit conversion between real numbers
    given by a factor F (a fraction).

    Relation:

        $$
          \fun \cdot \text{factor} \leq \res
        $$


    Attributes:

        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        factor: The fraction $\text{factor}$

    """

    opspace: Poset
    factor: Fraction


@dataclass
class AmbientConversion(PrimitiveDP):
    r"""
    A "conversion" between two posets $\F, \R$ that are subposets of a common ambient poset $\common$.

    Relation:

        $$
          \fun \leq_{\common}  \res
        $$

        where $\common$ is the common ambient poset.

    Attributes:

        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        common: The common ambient poset $\common$

    """

    common: Poset


@dataclass
class IdentityDP(PrimitiveDP):
    r"""
    This is the identity DP ($\F = \R$)

    Relation:

        $$
          \fun \leq \res
        $$


    Attributes:

        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$


    Note:

        It can be seen as a special case
        of [AmbientConversion][act4e_mcdp.primitivedps.AmbientConversion]
        where $\common = \F = \R$.
    """


@dataclass
class DPLoop2(PrimitiveDP):
    r""" """
    dp: PrimitiveDP


@dataclass
class Limit(PrimitiveDP):
    r"""
    Implements a bound on the functionality.

    This is the dual of [Constant][act4e_mcdp.primitivedps.Constant].

    Relation:

        $$
          \fun \leq  c
        $$

    Note that the resources $\res$ do not appear in the relation.
    As long as the functionality is below the limit, the resources can be anything.

    Attributes:

        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        c: The constant $c$

    """

    c: ValueFromPoset


@dataclass
class Constant(PrimitiveDP):
    r"""
    Implements a bound on the resources.

    This is the dual of [Limit][act4e_mcdp.primitivedps.Limit].

    Relation:

        $$
          c \leq  \res
        $$

        Note that the functionality $\fun$ do not appear in the relation.
        As long as the resources is above the limit, the functionality can be anything.

    Attributes:

        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        c: The constant $c$

    """

    c: ValueFromPoset


@dataclass
class EntryInfo:
    r"""
    Describes $\fun^{\max}_{\imp}$ and $\res^{\min}_{\imp}$ for an implementation.


    Attributes:
        f_max: The maximum functionality $\fun^{\max}_{\imp}$
        r_min: The minimum resources $\res^{\min}_{\imp}$

    """
    f_max: object
    r_min: object


@dataclass
class CatalogueDP(PrimitiveDP):
    r"""
    Implements a catalogue.

    The available implementations are strings and each of them has a (max) functionality and a (min) resource.

    Relation:

        $$
           \bigvee_{\imp \in \impspace}   ( \fun \leq \fun^{\max}_{\imp}) \wedge (\res^{\min}_{\imp} \leq
           \res)
        $$

        where $\impspace$ is the set of implementations and $\fun^{\max}_{\imp}, \res^{\min}_{\imp}$ are
        the functionality and resources of the implementation $\imp$.

    Attributes:

        F (Poset): The functionality poset $\F$
        R (Poset): The resources poset $\R$
        entries: A dictionary of entries.

    """

    entries: dict[str, EntryInfo]
