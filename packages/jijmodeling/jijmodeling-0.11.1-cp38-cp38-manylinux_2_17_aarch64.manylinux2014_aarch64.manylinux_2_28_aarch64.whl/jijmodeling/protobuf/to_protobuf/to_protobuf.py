from __future__ import annotations

import jijmodeling_schema as pb

from ulid import ULID

from jijmodeling.problem.problem import Problem
from jijmodeling.protobuf.to_protobuf.serialize_problem import serialize_problem

__version__ = "2023-03-20"


def to_protobuf(problem: Problem) -> bytes:
    """
    Convert a Problem object to a bytes object serialized by protobuf.

    Args:
        expr (Expression): a instance object of the `Problem` class

    Raises:
        TypeError: The error raises if the instance object cannot be converted to a protobuf object

    Returns:
        bytes: a bytes object
    """
    if isinstance(problem, Problem):
        # Create an empty `Header` message.
        message = pb.Header()

        # Make the id of the `Header` message.
        message.id = str(ULID())

        # Set the version of the JijModeling schema.
        message.version = __version__

        # Set the target message to the `header.value`.
        message.problem = serialize_problem(problem)
        return bytes(message)
    else:
        raise TypeError(
            f"{object.__class__.__name__} is not a Problem instance object."
        )
