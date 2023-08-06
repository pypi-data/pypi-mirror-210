from __future__ import annotations

import jijmodeling_schema as pb

from jijmodeling.expression.constraint import Penalty
from jijmodeling.protobuf.from_protobuf.deserialize_expr import deserialize_expr
from jijmodeling.protobuf.from_protobuf.deserialize_forall import deserialize_forall


def deserialize_penalty(penalty: pb.CustomPenaltyTerm) -> Penalty:
    """
    Convert a `Penalty` message into a `Penalty` object.

    Args:
        penalty (pb.Penalty): a `Penalty` message

    Returns:
        Penalty: a `Penalty` object
    """
    # Set the name of the penalty.
    name = penalty.name

    # Deserialize the penalty term.
    term = deserialize_expr(penalty.term)

    # Deserialize the list of forall.
    forall_list = [deserialize_forall(forall) for forall in penalty.forall_list]

    return Penalty(
        label=name,
        penalty_term=term,
        forall=forall_list,
    )
