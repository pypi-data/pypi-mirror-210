from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar

from .nameddps import NamedDP

__all__ = ["LowerSet", "SolverInterface", "UpperSet"]

X = TypeVar("X")


@dataclass
class UpperSet(Generic[X]):
    """
    Describes a finitely-supported **upper set** of elements of type X.

    Attributes:
        minima: A list of elements of type X, which are the minimal elements of the set.

    """

    minima: list[X]


@dataclass
class LowerSet(Generic[X]):
    """
    Describes a finitely-supported **lower set** of elements of type X.

    Attributes:
        maxima: A list of elements of type X, which are the minimal elements of the set.

    """

    maxima: list[X]


class SolverInterface(ABC):
    """
    An abstract class that describes the interface of a solver.

    """

    @abstractmethod
    def solve_FixFunMinRes(
        self, model: NamedDP, functionality_needed: Mapping[str, Any], /
    ) -> UpperSet[Mapping[str, Any]]:
        """

        Solves the problem of finding the minimal resources needed to satisfy a given functional requirement.

        The problem is defined by a model and a query. The model is a NamedDP, and the query is a mapping from
        the names of the resources to the values of the resources.

        The solution is a finitely-supported upper set.


        For example, this is what we expect from a solver for the empty model:

        ```python

            solver: SolverInterface = ...

            empty = CompositeNamedDP(functionalities={}, resources={}, nodes={}, connections=[])

            result: UpperSet = solver.solve_FixFunMinRes(empty, {})

            # We expect that the result is a list containing the empty dictionary

            assert list(result.minima) == [{}]

        ```

        In a more complex example, we can have a model describing the identity:

        ```python

            solver: SolverInterface = ...

            P = FinitePoset({'a', 'b'}, {('a', 'b')})

            identity = CompositeNamedDP(
                functionalities={'f1': P},
                resources={'r1': P},
                nodes={},
                connections=[
                    Connection(
                        source=ModelFunctionality('f1'),
                        target=ModelResource('r1')
                    )]
            )

            result: UpperSet = solver.solve_FixFunMinRes(identity, {'f1': 'a'})

            # We expect that the result is a list containing only one element

            assert list(result.minima) == [{'r1': 'a'}]
        ```


        Parameters:
            model: The model of the problem.
            functionality_needed: The functionality needed (key-value dictionary).

        Returns:

            A finitely-supported upper set of resources.
        """
        raise NotImplementedError

    @abstractmethod
    def solve_FixResMaxFun(
        self, model: NamedDP, resources_budget: Mapping[str, Any], /
    ) -> LowerSet[Mapping[str, Any]]:
        """
        This is the dual of solve_FixFunMinRes. It solves the problem of finding the maximal functionality
        that can be provided with a given budget of resources.


        For example, this is what we expect from a solver for the empty model:

        ```python

            solver: SolverInterface = ...

            empty = CompositeNamedDP(functionalities={}, resources={}, nodes={}, connections=[])

            result: LowerSet = solver.solve_FixResMaxFun(empty, {})

            # We expect that the result is a list containing the empty dictionary

            assert list(result.maxima) == [{}]

        ```

        Parameters:
            model: The model of the problem.
            resources_budget: The maximum budget that we have (key-value dictionary).

        Returns:

            A finitely-supported upper set of resources.


        """
        raise NotImplementedError
