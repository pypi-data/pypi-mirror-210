from __future__ import annotations

from typing import Tuple, Union

from jijmodeling.expression.condition import (
    CompareCondition,
    Condition,
    ConditionOperator,
    NoneCondition,
)
from jijmodeling.expression.expression import BinaryOperator, Expression, Number
from jijmodeling.expression.mathfunc import UnaryOperator
from jijmodeling.expression.sum import ReductionOperator
from jijmodeling.expression.type_annotations import ShapeElementType
from jijmodeling.expression.variables.deci_vars import Binary, Integer
from jijmodeling.expression.variables.jagged_array import JaggedArray
from jijmodeling.expression.variables.placeholders import ArrayShape, Placeholder
from jijmodeling.expression.variables.variable import Element, Range, Subscripts

ExpressionType = Union[Expression, Range]
ShapeType = Tuple[ShapeElementType, ...]


def is_same_expr(
    target: ExpressionType, pattern: ExpressionType, check_id: bool = True
) -> bool:
    # Check if the IDs are the same
    if check_id == True and target.uuid != pattern.uuid:
        return False

    # Check if the type of `target` is a subclass of the type of `pattern`
    if not isinstance(target, type(pattern)):
        return False
    if type(target) != type(pattern):
        return False

    # Case: Number
    if type(target) is Number and type(pattern) is Number:
        return is_same_number(target, pattern)
    # Case: Placeholder
    elif type(target) is Placeholder and type(pattern) is Placeholder:
        return is_same_placeholder(target, pattern, check_id)
    # Case: JaggedArray
    elif type(target) is JaggedArray and type(pattern) is JaggedArray:
        return is_same_jagged_array(target, pattern)
    # Case: ArrayShape
    elif type(target) is ArrayShape and type(pattern) is ArrayShape:
        return is_same_array_shape(target, pattern, check_id)
    # Case: Range
    elif type(target) is Range and type(pattern) is Range:
        return is_same_range(target, pattern, check_id)
    # Case: Element
    elif type(target) is Element and type(pattern) is Element:
        return is_same_element(target, pattern, check_id)
    # Case: Subscripts
    elif type(target) is Subscripts and type(pattern) is Subscripts:
        return is_same_subscripts(target, pattern, check_id)
    # Case: Binary
    elif type(target) is Binary and type(pattern) is Binary:
        return is_same_binary(target, pattern, check_id)
    # Case: Integer
    elif type(target) is Integer and type(pattern) is Integer:
        return is_same_integer(target, pattern, check_id)
    # Case: UnaryOperator
    elif isinstance(target, UnaryOperator) and isinstance(pattern, UnaryOperator):
        return is_same_unary_op(target, pattern, check_id)
    # Case: BinaryOperator
    elif isinstance(target, BinaryOperator) and isinstance(pattern, BinaryOperator):
        return is_same_binary_op(target, pattern, check_id)
    # Case: ReductionOperator
    elif isinstance(target, ReductionOperator) and isinstance(
        pattern, ReductionOperator
    ):
        return is_same_reduction_op(target, pattern, check_id)
    elif type(target) is ArrayShape and type(pattern) is ArrayShape:
        return is_same_arrayshape(target, pattern, check_id)
    # Case: No match
    else:
        raise TypeError(
            f"{target.__class__.__name__} is not supported in `is_same_expr`."
        )


def is_same_cond(target: Condition, pattern: Condition, check_id) -> bool:
    # Check if the IDs are the same
    if check_id == True and target.uuid != pattern.uuid:
        return False

    # Check if the type of `target` is a subclass of the type of `pattern`
    if not isinstance(target, type(pattern)):
        return False

    # Case: NonCondition
    if type(target) is NoneCondition and type(pattern) is NoneCondition:
        return True
    # Case: CompareCondition
    elif isinstance(target, CompareCondition) and isinstance(pattern, CompareCondition):
        return is_same_comparison_op(target, pattern, check_id)
    # Case: ConditionOperator
    elif isinstance(target, ConditionOperator) and isinstance(
        pattern, ConditionOperator
    ):
        return is_same_logical_op(target, pattern, check_id)
    # Case: No match
    else:
        raise TypeError(f"{target.__class__.__name__} is not supported.")


def is_same_number(target: Number, pattern: Number) -> bool:
    # Compare the following attributes:
    # - value
    # - dtype
    if target.value != pattern.value:
        return False
    elif target.dtype != pattern.dtype:
        return False
    else:
        return True


def is_same_arrayshape(target: ArrayShape, pattern: ArrayShape, check_id: bool) -> bool:
    # Compare the following attributes:
    # - array
    # - dim
    if is_same_expr(target.array, pattern.array, check_id):
        return False
    elif target.dimension != pattern.dimension:
        return False
    else:
        return True


def is_same_shape(target: ShapeType, pattern: ShapeType, check_id: bool) -> bool:
    if len(target) != len(pattern):
        return False

    for target_shape_elt, pattern_shape_elt in zip(target, pattern):
        # Check if the type of the element of `target` is different from the type of the element of `pattern`
        if type(target_shape_elt) is not type(pattern_shape_elt):
            return False
        # Case: the types of the elements of `target` and `pattern` are not equal to `ArrayShape`
        elif (
            type(target_shape_elt) is not ArrayShape
            and type(pattern_shape_elt) is not ArrayShape
        ):
            if not is_same_expr(target_shape_elt, pattern_shape_elt, check_id=check_id):
                return False
        # Case: the types of the elements of `target` and `pattern` are equal to `ArrayShape`
        elif check_id == True and target_shape_elt.uuid != pattern_shape_elt.uuid:
            return False
    return True


def is_same_placeholder(
    target: Placeholder, pattern: Placeholder, check_id: bool
) -> bool:
    # Compare the following attributes:
    # - label
    # - dim
    # - shape
    if target.label != pattern.label:
        return False
    elif target.dim != pattern.dim:
        return False
    else:
        return is_same_shape(target.shape, pattern.shape, check_id)


def is_same_jagged_array(target: JaggedArray, pattern: JaggedArray) -> bool:
    # Compare the following attributes:
    # - label
    # - dim
    if target.label != pattern.label:
        return False
    elif target.dim != pattern.dim:
        return False
    else:
        return True


def is_same_array_shape(
    target: ArrayShape, pattern: ArrayShape, check_id: bool
) -> bool:
    # Compare the following attributes:
    # - dimension
    # - array
    if target.dimension != pattern.dimension:
        return False
    else:
        return is_same_expr(target.array, pattern.array, check_id=check_id)


def is_same_range(target: Range, pattern: Range, check_id: bool) -> bool:
    # Compare the following attributes:
    # - start
    # - last
    return is_same_expr(target.start, pattern.start, check_id) and is_same_expr(
        target.last, pattern.last, check_id
    )


def is_same_element(target: Element, pattern: Element, check_id: bool) -> bool:
    # Comare the following attributes:
    # - label
    # - parent
    if target.label != pattern.label:
        return False
    else:
        return is_same_expr(target.parent, pattern.parent, check_id)


def is_same_subscripts(target: Subscripts, pattern: Subscripts, check_id: bool) -> bool:
    # Comare the following attributes:
    # - variable
    # - subscripts
    if not is_same_expr(target.variable, pattern.variable, check_id):
        return False
    elif len(target.subscripts) != len(pattern.subscripts):
        return False
    else:
        for target_subs, pattern_subs in zip(target.subscripts, pattern.subscripts):
            if not is_same_expr(target_subs, pattern_subs, check_id):
                return False
        return True


def is_same_binary(target: Binary, pattern: Binary, check_id: bool) -> bool:
    # Compare the following attributes:
    # - label
    # - shape
    if target.label != pattern.label:
        return False
    else:
        return is_same_shape(target.shape, pattern.shape, check_id)


def is_same_integer(target: Integer, pattern: Integer, check_id: bool) -> bool:
    # Compare the following attributes:
    # - label
    # - lower
    # - upper
    # - shape
    if target.label != pattern.label:
        return False
    elif not is_same_expr(target.lower, pattern.lower, check_id):
        return False
    elif not is_same_expr(target.upper, pattern.upper, check_id):
        return False
    else:
        return is_same_shape(target.shape, pattern.shape, check_id)


def is_same_unary_op(
    target: UnaryOperator, pattern: UnaryOperator, check_id: bool
) -> bool:
    # Compare the following attribute:
    # - operand
    return is_same_expr(target.operand, pattern.operand, check_id)


def is_same_binary_op(
    target: BinaryOperator, pattern: BinaryOperator, check_id: bool
) -> bool:
    # Compare the following attributes:
    # - left
    # - right
    return is_same_expr(target.left, pattern.left, check_id) and is_same_expr(
        target.right, pattern.right, check_id
    )


def is_same_reduction_op(
    target: ReductionOperator, pattern: ReductionOperator, check_id: bool
) -> bool:
    # Compare the following attributes:
    # - sum_index
    # - condition
    # - operand
    if not is_same_element(target.sum_index, pattern.sum_index, check_id):
        return False
    elif not is_same_cond(target.condition, pattern.condition, check_id):
        return False
    else:
        return is_same_expr(target.operand, pattern.operand, check_id)


def is_same_comparison_op(
    target: CompareCondition, pattern: CompareCondition, check_id: bool
) -> bool:
    # Compare the following attributes:
    # - left
    # - right
    return is_same_expr(target.left, pattern.left, check_id) and is_same_expr(
        target.right, pattern.right, check_id
    )


def is_same_logical_op(
    target: ConditionOperator, pattern: ConditionOperator, check_id: bool
) -> bool:
    # Compare the following attributes:
    # - left
    # - right
    return is_same_cond(target.left, pattern.left, check_id) and is_same_cond(
        target.right, pattern.right, check_id
    )
