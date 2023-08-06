from __future__ import annotations

import jijmodeling.expression.constraint as _constraint

from jijmodeling.match.condition_same import condition_same
from jijmodeling.match.expr_same import expr_same


def penalty_same(
    target: _constraint.Penalty, pattern: _constraint.Penalty, check_id: bool = True
) -> bool:
    # Is the same label?
    if target.label != pattern.label:
        return False
    # Is the same `with_multiplier`?
    if target.with_multiplier is not pattern.with_multiplier:
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
    # Is the same `penalty_term`?
    return expr_same(target.penalty_term, pattern.penalty_term, check_id)
