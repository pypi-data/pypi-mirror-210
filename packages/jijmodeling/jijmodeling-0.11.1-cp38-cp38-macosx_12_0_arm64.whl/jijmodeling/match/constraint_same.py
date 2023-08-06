from __future__ import annotations

import jijmodeling.expression.constraint as _constraint
import jijmodeling.expression.expression as _expression

from jijmodeling.match.condition_same import condition_same
from jijmodeling.match.expr_same import expr_same


def constraint_same(
    target: _constraint.Constraint,
    pattern: _constraint.Constraint,
    check_id: bool = True,
) -> bool:
    # Is the same label?
    if target.label != pattern.label:
        return False
    # Is the same `with_penalty`?
    if target.with_penalty != pattern.with_penalty:
        return False
    # Is the same `with_multiplier`?
    if target.with_multiplier != pattern.with_multiplier:
        return False
    # Is the same `auto_qubo`?
    if target.auto_qubo != pattern.auto_qubo:
        return False
    # Is the same `condition`?
    if condition_same(target.condition, pattern.condition, check_id) is False:
        return False
    # Is the same `left_lower`?
    if target.left_lower is None and pattern.left_lower is None:
        is_same_left_lower = True
    elif isinstance(target.left_lower, _expression.Expression) and isinstance(
        pattern.left_lower, _expression.Expression
    ):
        is_same_left_lower = expr_same(target.left_lower, pattern.left_lower, check_id)
    else:
        return False
    if is_same_left_lower is False:
        return False
    # Is the same `forall`?
    if len(target.forall) != len(pattern.forall):
        return False
    for target_forall, pattern_forall in zip(target.forall, pattern.forall):
        target_element, target_condition = target_forall
        pattern_element, pattern_condition = pattern_forall
        is_same_forall = expr_same(
            target_element, pattern_element, check_id
        ) and condition_same(target_condition, pattern_condition, check_id)

        if is_same_forall is False:
            return False
    return True
