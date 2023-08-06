from __future__ import annotations

import jijmodeling_schema as pb

from ulid import ULID

from jijmodeling.expression.constraint import Penalty
from jijmodeling.protobuf.to_protobuf.serialize_expr import serialize_expr
from jijmodeling.protobuf.to_protobuf.serialize_forall import serialize_forall


def serialize_penalty(penalty: Penalty) -> pb.CustomPenaltyTerm:
    """
    Convert a `Penalty` object into a `Penalty` message.

    Args:
        penalty (Penalty): a `Penalty` object

    Returns:
        pb.Penalty: a `Penalty` message
    """
    # Create an empty `Penalty` message
    message = pb.CustomPenaltyTerm()

    # Set the id of the penalty.
    message.id = str(ULID())

    # Set the name of the penalty.
    message.name = penalty.label

    # Deserialize the penalty term.
    message.term = serialize_expr(penalty.penalty_term)

    # Set the list of forall.
    message.forall_list.extend(
        [serialize_forall(element, condition) for element, condition in penalty.forall]
    )

    return message
