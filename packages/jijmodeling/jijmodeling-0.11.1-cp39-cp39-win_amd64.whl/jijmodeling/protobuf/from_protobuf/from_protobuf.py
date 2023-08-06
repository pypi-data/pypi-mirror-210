from __future__ import annotations

import jijmodeling_schema as pb

from jijmodeling.problem.problem import Problem
from jijmodeling.protobuf.from_protobuf.deserialize_problem import deserialize_problem


def from_protobuf(bytes: bytes) -> Problem:
    """
    Convert a bytes object in protobuf to a Problem object.

    Args:
        bytes (bytes): a bytes object in protobuf

    Returns:
        Problem: a Problem object
    """
    # Convert the bytes object into the `Header` message object.
    header = pb.Header.FromString(bytes)

    return deserialize_problem(header.problem)
