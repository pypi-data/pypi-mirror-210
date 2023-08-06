from __future__ import annotations

import jijmodeling_schema as pb

from ulid import ULID

from jijmodeling.expression.condition import Equal, LessThan, LessThanEqual
from jijmodeling.expression.constraint import Constraint
from jijmodeling.protobuf.to_protobuf.serialize_expr import serialize_expr
from jijmodeling.protobuf.to_protobuf.serialize_forall import serialize_forall


def serialize_constraint(constraint: Constraint) -> pb.Constraint:
    """
    Convert a `Constraint` object into a `Constraint` message.

    Args:
        constraint (Constraint): a `Constraint` object

    Returns:
        pb.Constraint: a `Constraint` message
    """
    # Create an empty `Constraint` message.
    message = pb.Constraint()

    # Set the id of the constraint.
    message.id = str(ULID())

    # Set the name of the constraint.
    message.name = constraint.label

    # Set the equality of the constraint.
    if isinstance(constraint.condition, (LessThan, LessThanEqual)):
        message.equality = pb.ConstraintEquality.LESS_THAN_EQUAL
    if isinstance(constraint.condition, Equal):
        message.equality = pb.ConstraintEquality.EQUAL

    # Serialize the left-hand side of the constraint.
    message.left = serialize_expr(constraint.condition.left)

    # Serialize the right-hand side of the constraint.
    message.right = serialize_expr(constraint.condition.right)

    # Set the list of forall.
    message.forall_list.extend(
        [
            serialize_forall(element, condition)
            for element, condition in constraint.forall
        ]
    )

    return message
