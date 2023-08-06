from __future__ import annotations

from jijmodeling.expression.condition import (
    AndOperator,
    CompareCondition,
    Condition,
    ConditionOperator,
    Equal,
    LessThan,
    LessThanEqual,
    NoneCondition,
    NotEqual,
    OrOperator,
    XorOperator,
)
from jijmodeling.expression.expression import (
    Add,
    BinaryOperator,
    Div,
    Expression,
    Mod,
    Mul,
    Number,
    Power,
)
from jijmodeling.expression.mathfunc import (
    AbsoluteValue,
    Ceil,
    Floor,
    Log2,
    UnaryOperator,
)
from jijmodeling.expression.prod import ProdOperator
from jijmodeling.expression.sum import ReductionOperator, SumOperator
from jijmodeling.expression.variables.placeholders import ArrayShape
from jijmodeling.expression.variables.variable import Range, Subscripts, Variable


def condition_latex_repr(expr: Condition) -> str:
    if isinstance(expr, CompareCondition):
        left = expr_latex_repr(expr.left)
        right = expr_latex_repr(expr.right)
        mark = r" \cdot "
        if isinstance(expr, Equal):
            mark = "="
        elif isinstance(expr, NotEqual):
            mark = r"\neq"
        elif isinstance(expr, LessThan):
            mark = "<"
        elif isinstance(expr, LessThanEqual):
            mark = r"\leq"
        return left + f" {mark} " + right
    elif isinstance(expr, ConditionOperator):
        left = condition_latex_repr(expr.left)
        right = condition_latex_repr(expr.right)
        mark = r" \cdot "
        if isinstance(expr, AndOperator):
            mark = r" \ \land \ "
        elif isinstance(expr, OrOperator):
            mark = r" \ \lor \ "
        elif isinstance(expr, XorOperator):
            mark = r" \ \veebar \ "
        return left + f"{mark}" + right
    else:
        return ""


def expr_latex_repr(expr: Expression) -> str:
    if expr._latex_repr is not None:
        return expr._latex_repr
    if isinstance(expr, Number):
        return str(expr.value)
    elif isinstance(expr, UnaryOperator):
        return _unary_latex_repr(expr)
    elif isinstance(expr, BinaryOperator):
        return _binary_latex_repr(expr)
    elif isinstance(expr, Variable):
        if isinstance(expr, ArrayShape):
            array = expr_latex_repr(expr.array)
            axis = str(expr.dimension)
            return rf"{array}_{{\mathrm{{shape}}({axis})}}"
        label = expr.label.replace("_", r"\_").replace("^", r"\_")
        if "_" in label:
            label = r"\mathrm{" + label + r"}"
        return label
    elif isinstance(expr, Subscripts):
        label = expr_latex_repr(expr.variable)
        subs = ",".join([expr_latex_repr(x) for x in expr.subscripts])
        return label + r"_{" + subs + r"}"
    elif isinstance(expr, ReductionOperator):
        return _reduction_latex_repr(expr)

    return rf"\mathrm{{ {str(expr)} }}"


def _unary_latex_repr(expr: UnaryOperator) -> str:
    operand = expr_latex_repr(expr.operand)
    if isinstance(expr, Ceil):
        return rf"\left\lceil {operand} \right\rceil"
    elif isinstance(expr, Floor):
        return rf"\left\lfloor {operand} \right\rfloor"
    elif isinstance(expr, AbsoluteValue):
        return rf"\left| {operand} \right|"
    elif isinstance(expr, Log2):
        return rf"\log_2 \left( {operand} \right)"


def _binary_latex_repr(expr: BinaryOperator) -> str:
    left = expr_latex_repr(expr.left)
    right = expr_latex_repr(expr.right)

    if isinstance(expr, Add):
        return _add_latex_repr(expr, left, right)
    elif isinstance(expr, Mul):
        return _mul_latex_repr(expr, left, right)
    elif isinstance(expr, Power):
        # Check if the base needs parentheses
        if isinstance(expr.left, (BinaryOperator, ReductionOperator)):
            left = rf"\left( {left} \right)"
        return rf"{left} ^ {{ {right} }}"
    elif isinstance(expr, Mod):
        # Check if the left hand side needs parentheses
        if isinstance(expr.left, BinaryOperator):
            left = rf"\left( {left} \right)"
        # Check if the left hand side needs parentheses
        if isinstance(expr.right, BinaryOperator):
            right = rf"\left( {right} \right)"
        return rf"{left} \mod {right}"
    elif isinstance(expr, Div):
        return rf"\frac{{ {left} }}{{ {right} }}"
    else:
        return r"\left(" + str(expr) + r"\right)"


def _add_latex_repr(expr: Add, left: str, right: str) -> str:
    symbol = "+"
    is_right_negative = False
    # check if the right hand side has a negative sign
    if (
        isinstance(expr.right, Mul)
        and isinstance(expr.right.left, Number)
        and expr.right.left.value == -1.0
    ):
        right = right[2:]
        symbol = "-"
        is_right_negative = True

    if isinstance(expr.right, Number) and expr.right.value < 0.0:
        num_abs = Number(expr.right.value * -1, dtype=expr.right.dtype)
        return f"{left} - {num_abs}"

    # check if the left hand side needs parentheses
    # ex: (a mod b) + right
    # ex: (a mod b) - right
    if isinstance(expr.left, Mod):
        left = rf"\left( {left} \right)"
    # check if the right hand side needs parentheses
    # ex: left + (a mod b)
    # ex: left - (a mod b)
    if isinstance(expr.right, Mod) or (
        is_right_negative and isinstance(expr.right.right, Mod)
    ):
        right = rf"\left( {right} \right)"

    return f"{left} {symbol} {right}"


def _mul_latex_repr(expr: Mul, left: str, right: str) -> str:
    if isinstance(expr.left, Number):
        coeff = expr.left.value
        if coeff == -1:
            # check if the right hand side needs parentheses
            if isinstance(expr.right, Add):
                return rf"- \left( {right} \right)"
            else:
                return f"- {right}"
        if coeff < 0:
            # check if the right hand side needs parentheses
            if isinstance(expr.right, Add):
                return rf"\left( {left} \right) \cdot \left( {right} \right)"
            else:
                return rf"\left( {left} \right) \cdot {right}"
    if isinstance(expr.right, Number):
        coeff = expr.right.value
        if coeff == -1:
            return f"- {right}"
        if coeff < 0:
            return rf"\left( {right} \right) \cdot {left}"

        # put coefficient in front of variable terms
        return rf"{right} \cdot {left}"

    parentheses_required_type = (Add, Mod)
    # check if the left hand side needs parentheses
    if isinstance(expr.left, parentheses_required_type):
        left = rf"\left( {left} \right)"
    # check if the right hand side needs parentheses
    if isinstance(expr.right, parentheses_required_type):
        right = rf"\left( {right} \right)"

    if left[0] == "-":
        left = rf"\left( {left} \right)"
    if right[0] == "-":
        right = rf"\left( {right} \right)"

    return left + r" \cdot " + right


def _reduction_latex_repr(expr: ReductionOperator) -> str:
    # select operator symbol in LaTeX
    if isinstance(expr, SumOperator):
        operator = r"\sum"
    elif isinstance(expr, ProdOperator):
        operator = r"\prod"
    # NOTE: When is this needed?
    else:
        operator = r"\Otimes"

    # make condition string in LaTeX
    condition = ""
    if not isinstance(expr.condition, NoneCondition):
        condition = rf",\ {condition_latex_repr(expr.condition)}"
    index = expr_latex_repr(expr.sum_index)

    # make index string in LaTeX
    # case: index belongs to range
    if isinstance(expr.sum_index.parent, Range):
        start = expr_latex_repr(expr.sum_index.parent.start)
        end = expr_latex_repr(expr.sum_index.parent.last - 1)
        operator = rf"{operator}_{{ {index} = {start}{condition} }}^{{ {end} }}"
    # case: index belongs to a set
    else:
        parent = expr_latex_repr(expr.sum_index.parent)
        operator = rf"{operator}_{{ {index} \in {parent}{condition} }}"

    operand = expr_latex_repr(expr.operand)

    # check if the operand needs parentheses
    parentheses_required_type = (Add, Mod)
    if isinstance(expr.operand, parentheses_required_type):
        return rf"{operator} \left( {operand} \right)"
    else:
        return rf"{operator} {operand}"
