from __future__ import annotations

import jijmodeling_schema as pb

from jijmodeling.expression.condition import Condition, NoneCondition
from jijmodeling.expression.variables.variable import Element
from jijmodeling.protobuf.to_protobuf.serialize_expr import (
    ProtobufSerializer,
    serialize_expr,
)


def serialize_forall(element: Element, condition: Condition) -> pb.Forall:
    """
    Convert a `forall` object into a `Forall` message.

    Args:
        element (Element): an `Element` object
        condition (Condition): a `Condition` object

    Returns:
        pb.Forall: a `Forall` message
    """
    # Create an empty `Forall` message.
    message = pb.Forall()

    # Serialize the forall index.
    serializer = ProtobufSerializer()
    message.index = serializer.make_element_message(element)
    message.index_domain_node_map = serializer.node_map

    # Serialize the condtion if it exists.
    if type(condition) is not NoneCondition:
        message.condition = serialize_expr(condition)

    return message
