from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from typing import Optional

__all__ = [
    "AmbientConversion",
    "CompositeNamedDP",
    "Connection",
    "DPSeries",
    "FinitePoset",
    "JoinNDP",
    "M_Ceil_DP",
    "M_FloorFun_DP",
    "M_Fun_AddConstant_DP",
    "M_Fun_AddMany_DP",
    "M_Fun_MultiplyConstant_DP",
    "M_Fun_MultiplyMany_DP",
    "M_Fun_MultiplyMany_DP",
    "M_Res_AddConstant_DP",
    "M_Res_AddMany_DP",
    "M_Res_MultiplyConstant_DP",
    "M_Res_MultiplyMany_DP",
    "MeetNDualDP",
    "MeetNDualDP",
    "ModelFunctionality",
    "ModelResource",
    "NamedDP",
    "NodeFunctionality",
    "NodeResource",
    "Numbers",
    "Numbers",
    "Poset",
    "PosetProduct",
    "PrimitiveDP",
    "SimpleWrap",
    "UnitConversion",
    "ValueFromPoset",
]


@dataclass
class Poset:
    pass


@dataclass
class Numbers(Poset):
    bottom: Decimal
    top: Decimal
    step: Decimal  # if 0 = "continuous"
    units: str  # if empty = dimensionless


@dataclass
class FinitePoset(Poset):
    elements: set[str]
    relations: set[tuple[str, str]]


@dataclass
class PosetProduct(Poset):
    subs: list[Poset]


@dataclass
class PrimitiveDP:
    description: Optional[str]
    F: Poset
    R: Poset


@dataclass
class DPSeries(PrimitiveDP):
    subs: list[PrimitiveDP]


@dataclass
class NamedDP:
    functionalities: dict[str, Poset]
    resources: dict[str, Poset]


@dataclass
class SimpleWrap(NamedDP):
    dp: PrimitiveDP


@dataclass
class NodeResource:
    node: str
    resource: str


@dataclass
class NodeFunctionality:
    node: str
    functionality: str


@dataclass
class ModelFunctionality:
    functionality: str


@dataclass
class ModelResource:
    resource: str


@dataclass
class Connection:
    source: ModelFunctionality | NodeResource
    target: ModelResource | NodeFunctionality


@dataclass
class CompositeNamedDP(NamedDP):
    nodes: dict[str, NamedDP]
    connections: list[Connection]


@dataclass
class ValueFromPoset:
    value: object
    poset: Poset


@dataclass
class M_Res_MultiplyConstant_DP(PrimitiveDP):
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Fun_MultiplyConstant_DP(PrimitiveDP):
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Res_AddConstant_DP(PrimitiveDP):
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Fun_AddMany_DP(PrimitiveDP):
    opspace: Poset


@dataclass
class M_Res_AddMany_DP(PrimitiveDP):
    opspace: Poset


@dataclass
class MeetNDualDP(PrimitiveDP):
    opspace: Poset


@dataclass
class JoinNDP(PrimitiveDP):
    opspace: Poset


@dataclass
class M_Fun_MultiplyMany_DP(PrimitiveDP):
    opspace: Poset


@dataclass
class M_Res_MultiplyMany_DP(PrimitiveDP):
    opspace: Poset


@dataclass
class M_Ceil_DP(PrimitiveDP):
    opspace: Poset


@dataclass
class M_FloorFun_DP(PrimitiveDP):
    opspace: Poset


@dataclass
class M_Fun_AddConstant_DP(PrimitiveDP):
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class M_Res_AddConstant_DP(PrimitiveDP):
    vu: ValueFromPoset
    opspace: Poset


@dataclass
class UnitConversion(PrimitiveDP):
    opspace: Poset
    factor: Fraction


@dataclass
class AmbientConversion(PrimitiveDP):
    pass
