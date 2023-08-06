from __future__ import annotations

from typing import Union

from jijmodeling.expression.condition import Condition
from jijmodeling.expression.expression import Expression
from jijmodeling.expression.variables.variable import Range
from jijmodeling.match.is_same_expr import ExpressionType, is_same_cond, is_same_expr


def expr_same(
    target: Union[ExpressionType, Condition],
    pattern: Union[ExpressionType, Condition],
    check_id: bool = True,
) -> bool:
    """
    Check if two expressions are the same.
    Args:
        target (Union[ExpressionType, Condition]): target expression
        pattern (Union[ExpressionType, Condition]): pattern expression
        check_id (bool): check if the uuid is the same, default is True
    Returns:
        bool: True if the expressions are the same
    """
    if isinstance(target, (Expression, Range)) and isinstance(
        pattern, (Expression, Range)
    ):
        return is_same_expr(target, pattern, check_id)
    elif isinstance(target, Condition) and isinstance(pattern, Condition):
        return is_same_cond(target, pattern, check_id)
    else:
        return False
