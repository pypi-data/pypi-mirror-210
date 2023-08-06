from __future__ import annotations

import itertools as it
import typing as tp

import typeguard as _typeguard

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.condition as _condition
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.extract as _extract
import jijmodeling.expression.sum as _sum
import jijmodeling.expression.variables.deci_vars as _deci_vars
import jijmodeling.expression.variables.variable as _variable

T = tp.TypeVar("T")


def type_check_bool(value, cls) -> bool:
    try:
        _typeguard.check_type(value, cls)
    except TypeError:
        return False
    else:
        return True


def extract_nodes(tree: _expression.Expression, cls: tp.Type[T]) -> tp.List[T]:
    """
    Extract specified class object from Expression tree.

    Args:
        tree (Expression): Target expression tree.
        cls (Type): Target class.

    Returns:
        List: `cls` object list are included in `tree`.

    Examples:
        ```python
        import jijmodeling as jm
        d = jm.Placheolder("d", dim=1)
        n = d.shape[0]
        x = jm.Binary("x", shape=(n, ))
        i = jm.Element("i", n)
        term = jm.Sum(i, d[i]*x[i])
        jm.extract_nodes(term, jm.DecisionVariable)
        # [x]
        ```
    """
    if type_check_bool(tree, cls):
        nodes = [tree]
    else:
        nodes = []
    for child in tree.children():
        nodes = nodes + extract_nodes(child, cls)  # type: ignore
    return nodes  # type: ignore


def get_order(expression: _expression.Expression) -> int:
    """
    Get an order of polynomial.

    For example, x_i * y_i + x_i -> 2 if x and y is a decision variable.

    Args:
        expression (Expression): expression

    Returns:
        int: Integer
    """
    if isinstance(expression, _deci_vars.DecisionVariable):
        return 1
    if isinstance(expression, _variable.Subscripts):
        if isinstance(expression.variable, _deci_vars.DecisionVariable):
            return 1
        else:
            return 0
    if isinstance(expression, (_expression.Add, _expression.Div)):
        child_order = [get_order(child) for child in expression.children()]
        return max(child_order)
    if isinstance(expression, _expression.Mul):
        child_order = [get_order(child) for child in expression.children()]
        return sum(child_order)
    if isinstance(expression, _expression.Power):
        base_order = get_order(expression.left)
        if base_order > 0:
            if isinstance(expression.right, _expression.Number):
                return base_order * int(expression.right.value)
            else:
                raise _exceptions.ModelingError("exponent should be number.")
    if isinstance(expression, _sum.SumOperator):
        return get_order(expression.operand)
    else:
        return 0


def expression_indices(
    expression: _expression.Expression,
) -> tp.List[_variable.Element]:
    """
    Extract all indices from the expression.

    Args:
        expression (Expression): expression

    Returns:
        List[Element]:
    """
    # TODO: implement expression_indices for each expression?
    indices: tp.List[_variable.Element]
    if isinstance(expression, _variable.Element):
        set_indices: tp.List[_variable.Element] = []
        for child in expression.children():
            set_indices = set_indices + expression_indices(child)
        indices = [expression] + set_indices
    elif isinstance(expression, _expression.Number):
        indices = []
    elif isinstance(expression, _variable.Variable):
        indices = []
    elif isinstance(expression, _variable.Subscripts):
        indices = []
        for subs in expression.subscripts:
            indices = indices + expression_indices(subs)
    elif isinstance(expression, _expression.Expression):
        indices = []
        for child in expression.children():
            if child is not None:
                indices = indices + expression_indices(child)
    else:
        raise TypeError(f"expression is Expression, not {type(expression)}")

    # check duplicated element
    el_label = []
    if isinstance(expression, _sum.ReductionOperator):
        el_label = [expression.sum_index.label]

    unique_indices: tp.List[_variable.Element] = []
    for index in indices:
        if index.label not in el_label:
            el_label.append(index.label)
            unique_indices.append(index)
    return unique_indices


def condition_indices(condition: _condition.Condition) -> tp.List[_variable.Element]:
    if isinstance(condition, _condition.CompareCondition):
        left_indices = expression_indices(condition.left)
        right_indices = expression_indices(condition.right)
        return left_indices + right_indices
    elif isinstance(condition, _condition.ConditionOperator):
        left_indices = condition_indices(condition.left)
        right_indices = condition_indices(condition.right)
        return left_indices + right_indices
    else:
        return []


def check_non_decision_variable(
    exp_list: tp.Iterable[_expression.Expression], error_msg: str
):
    """
    Check if list has decision variable or not.

    Args:
        exp_list (Iterable[Expression]): target iterator.
        error_msg (str): error message.

    Raises:
        CannotContainDecisionVarError: if list has decision variable.
    """
    for e in exp_list:
        variables = _extract.extract_variables(e)
        for v in variables:
            if isinstance(v, _deci_vars.DecisionVariable):
                raise _exceptions.CannotContainDecisionVarError(error_msg)


def flatten_binary_operator(
    expression: _expression.Expression,
    op_type: tp.Type[_expression.BinaryOperator] = _expression.Add,
) -> tp.List[_expression.Expression]:
    """
    Flatten `op_type` binary operator to list.
    This function flattens a given node to the following:
        node1 <> node2 <> node3 <> ... <> nodeN -> [node1, node2, node3, ..., nodeN]
    where <> is a specified binary operator by `op_type`.

    Args:
        expression (Expression): target expression.
        op_type (Type[BinaryOperator]): target binary operator.

    Returns:
        List[Expression]: list of expression. Each element is not binary operator.
    """
    if isinstance(expression, op_type):
        left = flatten_binary_operator(expression.left, op_type)
        right = flatten_binary_operator(expression.right, op_type)
        return list(it.chain.from_iterable([left, right]))
    else:
        return [expression]
