from __future__ import annotations

import jijmodeling_schema as pb

from jijmodeling.problem.problem import Problem, ProblemSense
from jijmodeling.protobuf.from_protobuf.deserialize_constraint import (
    deserialize_constraint,
)
from jijmodeling.protobuf.from_protobuf.deserialize_expr import deserialize_expr
from jijmodeling.protobuf.from_protobuf.deserialize_penalty import deserialize_penalty


def deserialize_problem(problem: pb.Problem) -> Problem:
    """
    Convert a `Problem` message into a `Problem` object.

    Args:
        problem (pb.Problem): a `Problem` message

    Returns:
        Problem: a `Problem` object
    """
    # Set sense of the problem.
    if problem.sense == pb.ProblemSense.MAX:
        sense = ProblemSense.MAXIMUM
    else:
        sense = ProblemSense.MINIMUM

    # Deserialize the objective function.
    objective = deserialize_expr(problem.objective_function)

    # Deserialize the constraints.
    constraints = {
        name: deserialize_constraint(constraint)
        for name, constraint in problem.constraint_map.items()
    }

    # Deserialize the penalties.
    penalties = {
        name: deserialize_penalty(penalty)
        for name, penalty in problem.custom_penalty_term_map.items()
    }

    return Problem(
        name=problem.name,
        sense=sense,
        objective=objective,
        constraints=constraints,
        penalties=penalties,
    )
