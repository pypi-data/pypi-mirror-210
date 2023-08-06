from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Collection, Generic, Mapping, TypeVar

from .structures import NamedDP

__all__ = ["LowerSet", "SolutionInterface", "UpperSet"]

X = TypeVar("X")


@dataclass
class UpperSet(Generic[X]):
    minima: Collection[X]


@dataclass
class LowerSet(Generic[X]):
    maxima: Collection[X]


class SolutionInterface(ABC):
    @abstractmethod
    def solve_FixFunMinRes(self, model: NamedDP, query: Mapping[str, Any]) -> UpperSet[Mapping[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def solve_FixResMaxFun(self, model: NamedDP, query: Mapping[str, Any]) -> LowerSet[Mapping[str, Any]]:
        raise NotImplementedError
