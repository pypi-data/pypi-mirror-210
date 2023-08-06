from __future__ import annotations

import typing as tp

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.condition as _condition
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.variables.deci_vars as _deci_vars
import jijmodeling.expression.variables.variable as _variable
import jijmodeling.problem.problem as _problem


def extract_variables(
    expression: _expression.Expression,
) -> tp.List[_variable.Variable]:
    """
    Extract variables.

    Args:
        expression (Expression): target expression

    Returns:
        List[Variable]: A list of variables included in the expression.

    Examples:
        ```python
        import jijmodeling as jm
        from jijmodeling.expression.extract import extract_variables
        a = jm.Placeholder("d", dim=2)
        n = a.shape[0]
        x = jm.Binary("x", shape=(n, ))
        i, j = jm.Element("i", n), jm.Element("j", n)
        term = jm.Sum([i, j], x[i] - s[i, j])
        extract_variables(term)
        # >>> [j, i, s, x, a, a_shape_0]
        ```
    """
    return list(_extract_var_dict(expression).values())


def extract_expressions(
    expression: _expression.Expression,
    pattern: tp.Callable[[_expression.Expression], bool],
) -> tp.List[_expression.Expression]:
    """
    Extract expressions.

    Args:
        expression (Expression): target expression
        pattern (Callable[Expression, bool]): pattern to extract

    Returns:
        List[Expression]: A list of expressions included in the expression.

    Examples:
        ```python
        import jijmodeling as jm
        from jijmodeling.expression.extract import extract_expressions
        a = jm.Placeholder("d", dim=2)
        n = a.shape[0]
        x = jm.Binary("x", shape=(n, ))
        i, j = jm.Element("i", n), jm.Element("j", n)
        s = jm.Binary("s", shape=(n, n))
        term = jm.Sum([i, j], x[i] - s[i, j])
        extract_expressions(term, lambda x: isinstance(x, jm.Element))
        # >>> [i, j]
        extract_expressions(term, lambda x: isinstance(x, jm.Binary))
        # >>> [x, s]
        extract_expressions(term, lambda x: isinstance(x, jm.Subscripts) and x.variable.label == "s")
        # >>> [s[i, j]]
        ```
    """
    return list(_extract_node_dict(expression, pattern).values())


def _extract_node_dict(
    expression: _expression.Expression,
    condition: tp.Callable[[_expression.Expression], bool],
) -> tp.Dict[str, _expression.Expression]:
    var_set = {}
    for child in expression.children():
        var_set.update(_extract_node_dict(child, condition))
    if condition(expression):
        var_set[expression.uuid] = expression
    return var_set


def _extract_var_dict(
    expression: _expression.Expression,
) -> tp.Dict[str, _variable.Variable]:
    return tp.cast(
        tp.Dict[str, _variable.Variable],
        _extract_node_dict(expression, lambda x: isinstance(x, _variable.Variable)),
    )


def extract_vars_from_cond(
    condition: _condition.Condition,
) -> tp.List[_variable.Variable]:
    return list(_extract_vars_from_cond_dict(condition).values())


def _extract_vars_from_cond_dict(
    condition: _condition.Condition,
) -> tp.Dict[str, _variable.Variable]:
    if isinstance(condition, _condition.CompareCondition):
        var_dict = _extract_var_dict(condition.left)
        var_dict.update(_extract_var_dict(condition.right))
        return var_dict

    elif isinstance(condition, _condition.ConditionOperator):
        var_dict = _extract_vars_from_cond_dict(condition.left)
        var_dict.update(_extract_vars_from_cond_dict(condition.right))
        return var_dict
    else:
        return {}


def extract_vars_from_problem(problem: _problem.Problem) -> tp.List[_variable.Variable]:
    return list(_extract_vars_from_problem_dict(problem).values())


def _extract_vars_from_problem_dict(
    problem: _problem.Problem,
) -> tp.Dict[str, _variable.Variable]:
    # Extracts all variables from the objective function
    variables = _extract_var_dict(problem.objective)

    # Extracts all variables from all the constraints
    for constraint in problem.constraints.values():
        variables.update(_extract_vars_from_cond_dict(constraint.condition))
        for index, condition in constraint.forall:
            variables.update(_extract_var_dict(index))
            variables.update(_extract_vars_from_cond_dict(condition))
        if constraint.left_lower is not None:
            variables.update(_extract_var_dict(constraint.left_lower))

    # Extracts all variables from all the user-defined penalty
    for penalty in problem.penalties.values():
        variables.update(_extract_var_dict(penalty.penalty_term))
        for index, condition in penalty.forall:
            variables.update(_extract_var_dict(index))
            variables.update(_extract_vars_from_cond_dict(condition))

    return variables


def check_unique_variable_label(expression: _expression.Expression):
    """
    Check unique variable label.

    Args:
        expression (Expression): target expression

    Returns:
        None: If the every variable label is unique.

    Raises:
        ModelingError: If label is not unique.
    """
    variables = extract_variables(expression)
    var_labels = []
    for v in variables:
        if v.label not in var_labels:
            var_labels.append(v.label)
        else:
            raise _exceptions.ModelingError(
                f"It seems that the variable {v.label} is defined twice. "
                + "Please check the label when defining the variable."
            )


def has_decivar(expression: _expression.Expression) -> bool:
    variables = extract_variables(expression)
    for v in variables:
        if isinstance(v, _deci_vars.DecisionVariable):
            return True
    return False


def condition_has_decivar(condition: _condition.Condition) -> bool:
    variables = extract_vars_from_cond(condition)
    for v in variables:
        if isinstance(v, _deci_vars.DecisionVariable):
            return True
    return False
