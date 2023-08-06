from __future__ import annotations

import jijmodeling_schema as pb

from ulid import ULID

from jijmodeling.problem.problem import Problem, ProblemSense
from jijmodeling.protobuf.to_protobuf.serialize_constraint import serialize_constraint
from jijmodeling.protobuf.to_protobuf.serialize_expr import serialize_expr
from jijmodeling.protobuf.to_protobuf.serialize_penalty import serialize_penalty


def serialize_problem(problem: Problem) -> pb.Problem:
    """
    Convert a `Problem` object into a `Problem` message.

    Args:
        problem (Problem): a `Problem` object

    Returns:
        pb.Problem: a `Problem` message
    """
    # Create an empty `Problem` message.
    message = pb.Problem()

    # Set the id of the problem.
    message.id = str(ULID())

    # Set the name of the problem.
    message.name = problem.name

    # Set sense of the problem.
    if problem.sense == ProblemSense.MINIMUM:
        message.sense = pb.ProblemSense.MIN
    else:
        message.sense = pb.ProblemSense.MAX

    # Serialize the objective function.
    message.objective_function = serialize_expr(problem.objective)

    # Serialize the constraints.
    for name, constraint in problem.constraints.items():
        message.constraint_map.update({name: serialize_constraint(constraint)})

    # Serialize the penalties.
    for name, penalty in problem.penalties.items():
        message.custom_penalty_term_map.update({name: serialize_penalty(penalty)})

    return message
