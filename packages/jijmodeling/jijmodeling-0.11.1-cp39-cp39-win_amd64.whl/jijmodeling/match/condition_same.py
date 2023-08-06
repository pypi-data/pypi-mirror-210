from __future__ import annotations

import jijmodeling.expression.condition as _condition

from jijmodeling.match.expr_same import expr_same


def condition_same(
    target: _condition.Condition, pattern: _condition.Condition, check_id: bool = True
) -> bool:
    if target.uuid == pattern.uuid:
        return True
    if not isinstance(target, type(pattern)):
        return False

    # case: CompareCondition
    if isinstance(target, _condition.CompareCondition) and isinstance(
        pattern, _condition.CompareCondition
    ):
        # Check the equality of left hand side
        is_left_same = expr_same(target.left, pattern.left, check_id)
        if is_left_same is False:
            return False

        # Check the equality of right hand side
        is_right_same = expr_same(target.right, pattern.right, check_id)
        if is_right_same is False:
            return False
        return True

    # case: ConditionOperator
    elif isinstance(target, _condition.ConditionOperator) and isinstance(
        pattern, _condition.ConditionOperator
    ):
        return condition_same(target.left, pattern.left, check_id) & condition_same(
            target.right, pattern.left, check_id
        )

    elif isinstance(target, _condition.NoneCondition) and isinstance(
        pattern, _condition.NoneCondition
    ):
        return True

    return False
