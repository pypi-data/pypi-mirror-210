from __future__ import annotations

from jijmodeling.match.constraint_same import constraint_same
from jijmodeling.match.expr_same import expr_same
from jijmodeling.match.penalty_same import penalty_same
from jijmodeling.problem.problem import Problem


def problem_same(target: Problem, pattern: Problem, check_id: bool = True) -> bool:
    # Is the same `name`?
    if target.name != pattern.name:
        return False
    # Is the same `sense`?
    if target.sense != pattern.sense:
        return False
    # Is the same `objective`?
    if expr_same(target.objective, pattern.objective, check_id) is False:
        return False
    # Is the same `constraints`?
    if len(target.constraints.items()) != len(pattern.constraints.items()):
        return False
    for target_key, target_constraint in target.constraints.items():
        if target_key not in pattern.constraints.keys():
            return False
        if (
            constraint_same(
                target_constraint, pattern.constraints[target_key], check_id
            )
            is False
        ):
            return False
    # Is the same `penalty`?
    if len(target.penalties.items()) != len(pattern.penalties.items()):
        return False
    for target_key, target_penalty in target.penalties.items():
        if target_key not in pattern.penalties.keys():
            return False
        if (
            penalty_same(target_penalty, pattern.penalties[target_key], check_id)
            is False
        ):
            return False

    return True
