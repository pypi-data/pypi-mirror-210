import typing as tp

import jijmodeling as jm

from jijmodeling.match.replace import replace_if


def expand_add(expr: jm.Expression) -> jm.Expression:
    """
    recursively replace the jm.Expression following the rules below:
    $$
    a  (c + d) \\rightarrow a  c + a  d
    $$
    $$
    (c + d)  a \\rightarrow c a + d a
    $$
    $$
    \sum_{...}^{...}(a + b) \\rightarrow \sum_{...}^{...}(a) + \sum_{...}^{...}(b)
    c * \sum_{...}^{...}(a) \\rightarrow \sum_{...}^{...}(c * a)
    \sum_{...}^{...}(a) * c \\rightarrow \sum_{...}^{...}(a * c)
    $$
    Args:
        expr (jm.Expression): target expression

    Returns:
        jm.Expression: expanded expression
    """

    # extract & replace
    def pattern_expand_add(expr: jm.Expression) -> tp.Optional[jm.Expression]:
        """pattern 1
        a * (c + d) -> a * c + a * d
        (c + d) * a -> c * a + d * a
        \sum_{...}^{...}(a + b) -> \sum_{...}^{...}(a) + \sum_{...}^{...}(b)
        c * \sum_{...}^{...}(a) -> \sum_{...}^{...}(c * a)
        \sum_{...}^{...}(a) * c -> \sum_{...}^{...}(a * c)
        """
        if isinstance(expr, jm.expression.expression.Mul):
            if isinstance(expr.right, jm.expression.expression.Add):
                a = expr.left
                c = expr.right.left
                d = expr.right.right
                return a * c + a * d

            elif isinstance(expr.left, jm.expression.expression.Add):
                a = expr.right
                c = expr.left.left
                d = expr.left.right
                return c * a + d * a
            elif isinstance(expr.right, jm.expression.sum.SumOperator):
                c = expr.left
                sum_expr = expr.right
                return jm.expression.sum.SumOperator(
                    sum_expr.sum_index, c * sum_expr.operand, sum_expr.condition
                )
            elif isinstance(expr.left, jm.expression.sum.SumOperator):
                c = expr.right
                sum_expr = expr.left
                return jm.expression.sum.SumOperator(
                    sum_expr.sum_index, sum_expr.operand * c, sum_expr.condition
                )

        if isinstance(expr, jm.expression.sum.SumOperator):
            if isinstance(expr.operand, jm.expression.expression.Add):
                operand_left = expr.operand.left
                operand_right = expr.operand.right
                return jm.expression.sum.SumOperator(
                    expr.sum_index, operand_left, expr.condition
                ) + jm.expression.sum.SumOperator(
                    expr.sum_index, operand_right, expr.condition
                )

        return None

    replaced_expr = expr

    # repeat until no more replacement
    while True:
        new_replaced_expr = replace_if(replaced_expr, pattern_expand_add)
        if jm.expr_same(replaced_expr, new_replaced_expr, check_id=False):
            break
        replaced_expr = new_replaced_expr

    return replaced_expr
