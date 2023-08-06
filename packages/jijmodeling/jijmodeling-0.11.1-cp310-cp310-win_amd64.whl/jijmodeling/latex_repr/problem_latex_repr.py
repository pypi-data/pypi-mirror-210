from __future__ import annotations

import re

from itertools import zip_longest

from jijmodeling.expression.condition import NoneCondition
from jijmodeling.expression.constraint import Constraint, Penalty
from jijmodeling.expression.extract import extract_vars_from_problem
from jijmodeling.expression.variables.deci_vars import Binary, DecisionVariable, Integer
from jijmodeling.expression.variables.variable import Range
from jijmodeling.latex_repr.latex_repr import condition_latex_repr, expr_latex_repr
from jijmodeling.problem.problem import Problem, ProblemSense


def range_latex_repr(el_range: Range):
    start_str = expr_latex_repr(el_range.start)
    last_str = expr_latex_repr(el_range.last - 1)
    latex_str: str = rf"\left\{{ {start_str} ,\ldots , {last_str} \right\}}"
    return latex_str


def escape_latex_special_character(text: str) -> str:
    """
    Replace characters that matches with the 10 latex special characters.

    There are 10 latex special characters:
    1. tilde `~`
    2. circumflex `^`
    3. backslash `\`
    4. percent sign `%`
    5. ampersand `&`
    6. dollar sign `$`
    7. number sign `#`
    8. underscore `_`
    9. left brace `{`
    10. right brace `}`

    https://tex.stackexchange.com/questions/34580/escape-character-in-latex/34586#34586

    If `latex` has some latex special characters, then replace the characters into other strings by following the below table:

    | name         | src  | dst                  |
    | ------------ | ---- | -------------------- |
    | backslash    | "\\" | "\textbackslash{}"   |
    | tilde        | "~"  | "\textasciitilde{}"  |
    | circumflex   | "^"  | "\textasciicircum{}" |
    | ampersand    | "&"  | "\\&"                |
    | percent sign | "%"  | "\\%"                |
    | dollar sign  | "$"  | "\\$"                |
    | number sign  | "#"  | "\\#"                |
    | underscore   | "_"  | "\\_"                |
    | left brace   | "{"  | "\\{"                |
    | right brace  | "}"  | "\\}"                |

    Args:
        text (str): string

    Returns:
        str: string without 10 latex special characters
    """
    latex_special_chars = "|".join(
        [r"\\", "~", r"\^", "&", "%", r"\$", "#", "_", "{", "}"]
    )

    replaced_special_chars = []
    for c in re.findall(latex_special_chars, text):
        if c == "\\":
            replaced_special_chars.append(r"\textbackslash{}")
        elif c == "~":
            replaced_special_chars.append(r"\textasciitilde{}")
        elif c == "^":
            replaced_special_chars.append(r"\textasciicircum{}")
        else:
            replaced_special_chars.append(rf"\{c}")

    text_without_special_chars = re.split(latex_special_chars, text)
    result = "".join(
        [
            no_special_char + replaced_special_char
            for no_special_char, replaced_special_char in zip_longest(
                text_without_special_chars, replaced_special_chars, fillvalue=""
            )
        ]
    )
    return result


def constraint_latex_repr(constraint: Constraint) -> str:
    name = escape_latex_special_character(constraint.label)
    latex_str = rf"\text{{{name}}} :\\ &\quad \quad "
    latex_str += condition_latex_repr(constraint.condition)
    latex_str += ","
    # case: condition has a forall condition
    if len(constraint.forall) > 0:
        for_all_str = ""
        condition_str = ""
        for index, condition in constraint.forall:
            parent_str = (
                range_latex_repr(index.parent)
                if isinstance(index.parent, Range)
                else expr_latex_repr(index.parent)
            )
            for_all_str += rf"\forall {expr_latex_repr(index)} \in {parent_str} "
            condition_str += (
                ""
                if isinstance(condition, NoneCondition)
                else condition_latex_repr(condition) + r"\land "
            )
        # for_all_str = for_all_str.rstrip(', ')
        latex_str += rf"\ {for_all_str}"

        condition_str = condition_str.rstrip(r"\land ")
        if condition_str != "":
            latex_str += rf" \ {condition_str}"
    return latex_str


def penalty_latex_repr(penalty: Penalty) -> str:
    name = escape_latex_special_character(penalty.label)
    latex_str = rf"\text{{{name}}} :\\ &\quad \quad "
    latex_str += expr_latex_repr(penalty.penalty_term)
    latex_str += ","

    # case: penalty has a forall condition
    if len(penalty.forall) > 0:
        for_all_str = ""
        condition_str = ""
        for index, condition in penalty.forall:
            parent_str = (
                range_latex_repr(index.parent)
                if isinstance(index.parent, Range)
                else expr_latex_repr(index.parent)
            )
            for_all_str += rf"\forall {expr_latex_repr(index)} \in {parent_str} "
            condition_str += (
                ""
                if isinstance(condition, NoneCondition)
                else condition_latex_repr(condition) + r"\land "
            )
        # for_all_str = for_all_str.rstrip(', ')
        latex_str += rf"\ {for_all_str}"

        condition_str = condition_str.rstrip(r"\land ")
        if condition_str != "":
            latex_str += rf" \ {condition_str}"

    return latex_str


def problem_latex_repr(problem: Problem) -> str:
    name = escape_latex_special_character(problem.name)
    latex_str = rf"\text{{Problem}} & \text{{: {name}}} \\"
    if problem.sense == ProblemSense.MAXIMUM:
        latex_str += rf"\max & \quad {problem.objective._make_latex()} \\"
    else:
        latex_str += rf"\min & \quad {problem.objective._make_latex()} \\"

    # case: Problem has more than one penalties.
    if len(problem.penalties) > 0:
        latex_str += r"\text{Penalties} & \\"
        # Shows all penalties.
        for penalty in problem.penalties.values():
            latex_str += rf"& {penalty_latex_repr(penalty)}\\[8pt]"

    # case: Problem has more than one constraints.
    if len(problem.constraints) > 0:
        latex_str += r"\text{s.t.} & \\"
        # show all constraints
        for _, constraint in problem.constraints.items():
            latex_str += rf"& {constraint_latex_repr(constraint)}\\[8pt]"

    latex_str += "&"

    # Extracts all decision variables from the Problem object.
    deci_var_list = {
        var.label: var
        for var in extract_vars_from_problem(problem)
        if isinstance(var, DecisionVariable)
    }

    # Checks if the problem does not have any decision variable
    if deci_var_list == {}:
        return latex_str

    used_decision_variable = ""
    for deci_var in deci_var_list.values():
        label = deci_var._make_latex()
        has_subscripts = deci_var.dim > 0
        if has_subscripts:
            subscripts = ""
            for i in range(deci_var.dim):
                subscripts += rf"i_{{{format(str(i))}}},"
            subscripts = subscripts.rstrip(",")

            used_decision_variable += rf"{label}_{{{subscripts}}}"
        else:
            used_decision_variable += label

        # case: Binary
        if isinstance(deci_var, Binary):
            used_decision_variable += r" \in \{0, 1\}"
        # case: Integer
        elif isinstance(deci_var, Integer):
            used_decision_variable += r" \in \mathbb{Z}"

        used_decision_variable += r",\ "
    used_decision_variable = used_decision_variable.rstrip(r",\ ")

    return rf"{latex_str} {used_decision_variable}"
