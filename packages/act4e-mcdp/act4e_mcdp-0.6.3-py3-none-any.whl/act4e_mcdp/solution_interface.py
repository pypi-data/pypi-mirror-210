from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar

from .nameddps import NamedDP
from .primitivedps import PrimitiveDP

__all__ = [
    "DPSolverInterface",
    "Interval",
    "LowerSet",
    "MCDPSolverInterface",
    "UpperSet",
]

X = TypeVar("X")


@dataclass
class UpperSet(Generic[X]):
    """
    Describes a finitely-supported **upper set** of elements of type X.

    Attributes:
        minimals: A list of elements of type X, which are the minimal elements of the set.

    """

    minimals: list[X]


@dataclass
class LowerSet(Generic[X]):
    """
    Describes a finitely-supported **lower set** of elements of type X.

    Attributes:
        maximals: A list of elements of type X, which are the minimal elements of the set.

    """

    maximals: list[X]


@dataclass(kw_only=True)
class Interval(Generic[X]):
    """
    Describes an optimistic-pessimistic interval for a quantity of type X.

    The two values can be the same if there is no uncertainty.

    Attributes:
        pessimistic: The pessimistic value
        optimistic: The optimistic value

    """

    pessimistic: X
    optimistic: X


class DPSolverInterface(ABC):
    """
    An abstract class that describes the interface of a solver for DPs.

    """

    @abstractmethod
    def solve_dp_FixFunMinRes(
        self,
        dp: PrimitiveDP,
        functionality_needed: object,
        /,
        resolution_optimistic: int = 0,
        resolution_pessimistic: int = 0,
    ) -> Interval[UpperSet[object]]:
        r"""

        Solves the problem of finding the minimal resources needed to satisfy a given functional requirement.

        The problem is defined by a DP and a query. The model is a DP, and the query is an
        object that belongs to the poset $\F$ of the functionalities of the DP.

        The solution is an interval of upper sets (of objects of $\R$).


        For example, this is what we expect from a solver for an empty catalogue:

        ```python

            solver: SolverInterface = ...

            P = FinitePoset({'a', 'b'}, {('a', 'b')})

            empty_catalogue = CatalogueDP(F=P, R=P, entries={})

            result = solver.solve_dp_FixFunMinRes(empty, 'a')

            assert result.pessimistic == result.optimistic == UpperSet([])

        ```
        For example, for the identity:


        ```python

            solver: SolverInterface = ...

            P = FinitePoset({'a', 'b'}, {('a', 'b')})

            empty_catalogue = IdentityDP(F=P, R=P)

            result = solver.solve_dp_FixFunMinRes(empty, 'a')

            assert result.pessimistic == result.optimistic == UpperSet(['a'])

        ```

        Parameters:
            dp: A design problem.
            functionality_needed: The functionality needed.
            resolution_optimistic: An integer returning the resolution of the optimistic answer, to
                be used in the case of DPs that are not computable.

            resolution_pessimistic: Same for the pessimistic answer.



        Returns:

            An interval of upper sets.
        """
        raise NotImplementedError

    @abstractmethod
    def solve_dp_FixResMaxFun(
        self,
        dp: PrimitiveDP,
        resource_budget: object,
        /,
        resolution_optimistic: int = 0,
        resolution_pessimistic: int = 0,
    ) -> Interval[LowerSet[object]]:
        """
        Solves the problem of finding the maximal functionality that can be provided with a given budget of
        resources.
        It is the dual of solve_dp_FixFunMinRes.

        Parameters:
            dp: A design problem.
            resource_budget: The resources available.
            resolution_optimistic: An integer returning the resolution of the optimistic answer,
                to be used in the case of DPs that are not computable.
            resolution_pessimistic: Same thing, for the pessimistic answer.

        Returns:

            An interval of lower sets.
        """


class MCDPSolverInterface(ABC):
    """An abstract class that describes the interface of a solver for NamedDPs."""

    @abstractmethod
    def solve_mcdp_FixFunMinRes(
        self,
        graph: NamedDP,
        functionality_needed: Mapping[str, Any],
        /,
        resolution_optimistic: int = 0,
        resolution_pessimistic: int = 0,
    ) -> Interval[UpperSet[Mapping[str, Any]]]:
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
            graph: The model of the problem.
            functionality_needed: The functionality needed (key-value dictionary).
            resolution_optimistic: An integer returning the resolution of the optimistic answer,
                to be used in the case of DPs that are not computable.
            resolution_pessimistic: Same thing, for the pessimistic answer.

        Returns:

            An interval of upper sets.

        """
        raise NotImplementedError

    @abstractmethod
    def solve_mcdp_FixResMaxFun(
        self,
        graph: NamedDP,
        resources_budget: Mapping[str, Any],
        /,
        resolution_optimistic: int = 0,
        resolution_pessimistic: int = 0,
    ) -> Interval[LowerSet[Mapping[str, Any]]]:
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
            graph: The model of the problem.
            resources_budget: The maximum budget that we have (key-value dictionary).
            resolution_optimistic: An integer returning the resolution of the optimistic answer,
                to be used in the case of DPs that are not computable.
            resolution_pessimistic: Same thing, for the pessimistic answer.

        Returns:

             An interval of lower sets.


        """
        raise NotImplementedError
