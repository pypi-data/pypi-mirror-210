import typing as tp

from functools import singledispatch

import jijmodeling as jm
import jijmodeling.expression.condition as jc

from jijmodeling.expression.extract import extract_expressions
from jijmodeling.match.expr_same import expr_same


def replace(
    expr: jm.Expression, target: jm.Expression, source: jm.Expression, check_id: bool
) -> jm.Expression:
    """
    replace expression (from `target` element to `source` one)
    This function selects the target element from the expression and recursively replaces it with the source element.

    Args:
        expr (jm.Expression): expression
        target (jm.Expression): target sub tree
        source (jm.Expression): new sub tree
        check_id (bool): replace only if the uuid is the same

    Returns:
        jm.Expression: replaced sub tree

    Examples:
        ```python
        import jijmodeling as jm
        n = jm.Placeholder("n")
        i = jm.Element("i", n)
        x = jm.Binary("x", shape=(n, n))
        x_i = x[i]
        expr = jm.Sum(i, x_i)
        u = jm.Integer("u", shape=(n,), lower=0, upper=10)
        k = jm.Placeholder("k")
        j = jm.Element("j", k)
        y = jm.Placeholder("y", shape=(n, k))
        replaced = replace(expr, x_i, jm.Sum(j, u[i]*y[i,j]), check_id=True)
        print(replaced)
        Sum_{i=0}^{n}(Sum_{j=0}^{k}(u[i]*y[i,j]))
        ```

        ```python
        import jijmodeling as jm
        n = jm.Placeholder("n")
        i = jm.Element("i", n)
        x = jm.Binary("x", shape=(n, n))
        expr = jm.Sum(i, x[i])
        u = jm.Integer("u", shape=(n,), lower=0, upper=10)
        k = jm.Placeholder("k")
        j = jm.Element("j", k)
        y = jm.Placeholder("y", shape=(n, k))
        replaced = replace(expr, x[i], jm.Sum(j, u[i]*y[i,j]), check_id=False) # check_id=False にすると、uuidが異なっていても置換できる
        print(replaced)
        Sum_{i=0}^{n}(Sum_{j=0}^{k}(u[i]*y[i,j]))
        ```
    """
    if expr_same(expr, target, check_id):
        return source

    return _replace(expr, target, source, check_id)


def replace_if(
    expr: jm.Expression,
    replace_func: tp.Callable[[jm.Expression], tp.Optional[jm.Expression]],
):
    """recursively replace expression if `replace_func` returns `jm.Expression` object. Otherwise, the expression is not replaced.
    This function does the following process only once:
    1. extract all the expressions that satisfies `replace_func`
    2. replace the expression with the result of `replace_func`

    Args:
        expr (jm.Expression): expression
        replace_func (tp.Callable[[jm.Expression], tp.Optional[jm.Expression]]): `jm.Expression` object is given and `jm.Expression` object is returned if the expression is replaced.

    Returns:
        jm.Expression: replaced expression
    """
    # list all expression to be replaced
    replaced_expr = expr
    is_replaced = lambda expr: replace_func(expr) is not None
    replace_candidates = extract_expressions(replaced_expr, is_replaced)
    new_replaced_expr = replaced_expr
    for candidate in replace_candidates:
        new_replaced_expr = replace(
            new_replaced_expr,
            candidate,
            tp.cast(jm.Expression, replace_func(candidate)),
            check_id=False,
        )

    return new_replaced_expr


@singledispatch
def _replace(
    expr: jm.Expression, target: jm.Expression, source: jm.Expression, check_id: bool
) -> jm.Expression:
    raise TypeError(f"{type(expr)} is not supported in `replace`.")


# List all the types that are inherited from `jm.Expression` and register them to `_replace` function.
@_replace.register
def _(
    expr: jm.ArrayShape, target: jm.Expression, source: jm.Expression, check_id: bool
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source
    if isinstance(source, (jm.Variable, jm.Subscripts)) and expr_same(
        expr.array, target, check_id
    ):
        return source.shape[expr.dim]
    return expr


@_replace.register
def _(
    expr: jm.expression.Number,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source
    return expr


@_replace.register
def _(
    expr: jm.expression.BinaryOperator,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source

    cls = type(expr)
    replaced_left = _replace(expr.left, target, source, check_id)
    replaced_right = _replace(expr.right, target, source, check_id)
    return cls(replaced_left, replaced_right)


@_replace.register
def _(
    expr: jm.expression.UnaryOperator,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source

    cls = type(expr)
    replaced = _replace(expr, target, source, check_id)
    return cls(replaced)


@_replace.register
def _(
    expr: jm.expression.sum.ReductionOperator,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source

    replaced_sum_index = tp.cast(
        jm.Element, _replace(expr.sum_index, target, source, check_id)
    )
    replaced_operand = _replace(expr.operand, target, source, check_id)
    replaced_condition = _replace_condition(expr.condition, target, source, check_id)
    cls = type(expr)
    return cls(replaced_sum_index, replaced_operand, replaced_condition)


@_replace.register
def _(
    expr: jm.Variable, target: jm.Expression, source: jm.Expression, check_id: bool
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source
    return expr


@_replace.register
def _(
    expr: jm.Subscripts, target: jm.Expression, source: jm.Expression, check_id: bool
) -> jm.Expression:
    if expr_same(expr, target, check_id):
        return source
    replaced_variable = tp.cast(
        jm.Variable, _replace(expr.variable, target, source, check_id)
    )
    replaced_subscripts = [
        _replace(s, target, source, check_id) for s in expr.subscripts
    ]
    cls = type(expr)
    return cls(replaced_variable, replaced_subscripts)


@singledispatch
def _replace_condition(
    condition: jc.Condition,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jc.Condition:
    raise TypeError(f"{type(condition)} is not supported in `replace`.")


@_replace_condition.register
def _(
    condition: jc.NoneCondition,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jc.Condition:
    return condition


@_replace_condition.register
def _(
    condition: jc.CompareCondition,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jc.Condition:
    replaced_left = _replace(condition.left, target, source, check_id)
    replaced_right = _replace(condition.right, target, source, check_id)
    cls = type(condition)
    return cls(replaced_left, replaced_right)


@_replace_condition.register
def _(
    condition: jc.ConditionOperator,
    target: jm.Expression,
    source: jm.Expression,
    check_id: bool,
) -> jc.Condition:
    replaced_left = _replace_condition(condition.left, target, source, check_id)
    replaced_right = _replace_condition(condition.right, target, source, check_id)
    cls = type(condition)
    return cls(replaced_left, replaced_right)
