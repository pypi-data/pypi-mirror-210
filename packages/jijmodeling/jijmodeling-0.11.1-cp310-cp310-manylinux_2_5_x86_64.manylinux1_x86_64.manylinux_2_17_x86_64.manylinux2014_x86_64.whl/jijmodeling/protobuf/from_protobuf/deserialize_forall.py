from __future__ import annotations

from typing import Optional, Tuple

import jijmodeling_schema as pb

from jijmodeling.expression.condition import Condition
from jijmodeling.expression.variables.variable import Element
from jijmodeling.protobuf.from_protobuf.deserialize_expr import (
    ProtobufDeserializer,
    deserialize_expr,
)


def deserialize_forall(forall: pb.Forall) -> Tuple[Element, Optional[Condition]]:
    """
    Convert a `Forall` message into a `forall` object.

    Args:
        forall (pb.Forall): a `Forall` message

    Returns:
        Tuple[Element, Optional[Condition]]: objects to make the `forall` object
    """
    # Deserialize the element.
    deserializer = ProtobufDeserializer(forall.index_domain_node_map)
    element = deserializer.deserialize_element(forall.index)

    # Set the condition expression.
    has_condition = forall.condition.expr_node_map != {}
    condition = deserialize_expr(forall.condition) if has_condition else None

    return (element, condition)
