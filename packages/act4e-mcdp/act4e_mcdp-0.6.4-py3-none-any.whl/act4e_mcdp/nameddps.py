from dataclasses import dataclass

from .posets import Poset
from .primitivedps import PrimitiveDP

__all__ = [
    "CompositeNamedDP",
    "Connection",
    "ModelFunctionality",
    "ModelResource",
    "NamedDP",
    "NodeFunctionality",
    "NodeResource",
    "SimpleWrap",
]


@dataclass
class NamedDP:
    r"""
    Generic interface of a NamedDP.

    Attributes:
        functionalities: a dictionary of functionalities. The order is significant.
        resources: a dictionary of resources. The order is significant.


    """
    functionalities: dict[str, Poset]
    resources: dict[str, Poset]


@dataclass
class SimpleWrap(NamedDP):
    r"""
    A simple wrapper that wraps a [PrimitiveDP][act4e_mcdp.primitivedps.PrimitiveDP].


    Note that a [PrimitiveDP][act4e_mcdp.primitivedps.PrimitiveDP] does not have
    a notion of "functionality names" and "resource names". When we wrap it in a SimpleWrap,
    we can associate names to them.


    Attributes:
        functionalities (dict[str, Poset]): a dictionary of functionalities. The order is significant.
        resources (dict[str, Poset]): a dictionary of resources. The order is significant.
        dp: the wrapped DP.


    """

    dp: PrimitiveDP


@dataclass
class NodeResource:
    """
    A resource of a node.
    Used by the [Connection][act4e_mcdp.nameddps.Connection] class.

    Attributes:
        node: the node name
        resource: the resource name

    """

    node: str
    resource: str


@dataclass
class NodeFunctionality:
    """
    A functionality of a node.
    Used by the [Connection][act4e_mcdp.nameddps.Connection] class.

    Attributes:
        node: the node name
        functionality: the functionality name
    """

    node: str
    functionality: str


@dataclass
class ModelFunctionality:
    """
    A functionality of the entire diagram.
    Used by the [Connection][act4e_mcdp.nameddps.Connection] class.

    Attributes:
        functionality: the functionality name
    """

    functionality: str


@dataclass
class ModelResource:
    """
    A resource of the entire diagram.
    Used by the [Connection][act4e_mcdp.nameddps.Connection] class.

    Attributes:
        resource: the resource name

    """

    resource: str


@dataclass
class Connection:
    r"""
    A connection in a co-design graph.

    Note that the **source** of a connection can be either:
    - a [ModelFunctionality][act4e_mcdp.nameddps.ModelFunctionality]: a **functionality** of the entire
    diagram
    - a [NodeResource][act4e_mcdp.nameddps.NodeResource]: a **resource** of a node.

    Note that the **target** of a connection can be either:
    - a [ModelResource][act4e_mcdp.nameddps.ModelResource]: a **resource** of the entire diagram
    - a [NodeFunctionality][act4e_mcdp.nameddps.NodeFunctionality]: a **functionality** of a node.

    Attributes:
        source: the source of the connection
        target: the target of the connection

    """
    source: ModelFunctionality | NodeResource
    target: ModelResource | NodeFunctionality


@dataclass
class CompositeNamedDP(NamedDP):
    r"""
    Description of a composite NamedDP.

    The nodes are in `nodes` dictionary and the connections are in `connections` list.
    See the class [Connection][act4e_mcdp.nameddps.Connection] for more details about the
    interconnections.

    This is how you would describe an empty diagram:

    ```python
    empty = CompositeNamedDP(functionalities={}, resources={},
                             nodes={}, connections=[])
    ```

    This corresponds to the DP from 1 to 1 which is always true.


    This is how you would describe a diagram with two empty nodes:

    ```python
    two_inside = CompositeNamedDP(
        functionalities={}, resources={},
        nodes={
            'one': empty,
            'two': empty,
         }, connections=[])
    ```

    This is how you would describe a diagram with one functionality and resource
    connected directly (identity):

    ```python
    P = FinitePoset({'a', 'b'}, {('a', 'b')})

    two_inside = CompositeNamedDP(
        functionalities={'f1': P},
        resources={'r1': P},
        nodes={},
        connections=[
            Connection(
                source=ModelFunctionality('f1'),
                target=ModelResource('r1')
            )]
    )
    ```

    Attributes:
       functionalities (dict[str, Poset]): a dictionary of functionalities
       resources (dict[str, Poset]): a dictionary of resources
       nodes: the nodes inside the graph
       connections: the connections between nodes

    """

    nodes: dict[str, NamedDP]
    connections: list[Connection]
