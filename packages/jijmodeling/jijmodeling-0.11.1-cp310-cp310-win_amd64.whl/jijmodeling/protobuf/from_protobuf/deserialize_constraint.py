from __future__ import annotations

import jijmodeling_schema as pb

from jijmodeling.expression.constraint import Constraint
from jijmodeling.protobuf.from_protobuf.deserialize_expr import deserialize_expr
from jijmodeling.protobuf.from_protobuf.deserialize_forall import deserialize_forall


def deserialize_constraint(constraint: pb.Constraint) -> Constraint:
    """
    Convert a `Constraint` message into a `Constraint` object.

    Args:
        constraint (pb.Constraint): a `Constraint` message

    Returns:
        Constraint: a `Constraint` object
    """
    # Set the name of the constraint.
    name = constraint.name

    # Deserialize the left-hand side of the constraint.
    left = deserialize_expr(constraint.left)

    # Deserialize the right-hand side of the constraint.
    right = deserialize_expr(constraint.right)

    if constraint.equality == pb.ConstraintEquality.EQUAL:
        expr = left == right
    elif constraint.equality == pb.ConstraintEquality.LESS_THAN_EQUAL:
        expr = left <= right
    elif constraint.equality == pb.ConstraintEquality.GREATER_THAN_EQUAL:
        expr = right <= left

    # Deserialize the list of forall.
    forall_list = [deserialize_forall(forall) for forall in constraint.forall_list]

    return Constraint(
        label=name,
        condition=expr,
        forall=forall_list,
    )
