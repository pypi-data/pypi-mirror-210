from __future__ import annotations

from jijmodeling.expression.condition import (
    AndOperator,
    Equal,
    LessThan,
    LessThanEqual,
    NoneCondition,
    OrOperator,
    XorOperator,
)
from jijmodeling.expression.constraint import Constraint, Penalty
from jijmodeling.expression.expression import (
    Add,
    Div,
    Expression,
    Mod,
    Mul,
    Number,
    Power,
)
from jijmodeling.expression.mathfunc import AbsoluteValue, Ceil, Floor, Log2, Max, Min
from jijmodeling.expression.prod import ProdOperator
from jijmodeling.expression.sum import SumOperator
from jijmodeling.expression.variables.deci_vars import Binary, Integer
from jijmodeling.expression.variables.jagged_array import JaggedArray
from jijmodeling.expression.variables.placeholders import ArrayShape, Placeholder
from jijmodeling.expression.variables.variable import Element, Range, Subscripts
from jijmodeling.problem import Problem, ProblemSense

_OLD_NAME_TO_CLASS = {
    "jijmodeling.expression.variables.placeholders.Placeholder": Placeholder,
    "jijmodleing.expression.variables.jagged_array.JaggedArray": JaggedArray,
    "jijmodeling.expression.variables.variable.Subscripts": Subscripts,
    "jijmodeling.expression.variables.variable.Element": Element,
    "jijmodeling.expression.variables.variable.Range": Range,
    "jijmodeling.expression.variables.placeholders.ArrayShape": ArrayShape,
    "jijmodeling.expression.expression.Number": Number,
    "jijmodeling.expression.expression.Add": Add,
    "jijmodeling.expression.expression.Mul": Mul,
    "jijmodeling.expression.expression.Div": Div,
    "jijmodeling.expression.expression.Power": Power,
    "jijmodeling.expression.expression.Mod": Mod,
    "jijmodeling.expression.mathfunc.AbsoluteValue": AbsoluteValue,
    "jijmodeling.expression.mathfunc.Max": Max,
    "jijmodeling.expression.mathfunc.Min": Min,
    "jijmodeling.expression.mathfunc.Ceil": Ceil,
    "jijmodeling.expression.mathfunc.Floor": Floor,
    "jijmodeling.expression.mathfunc.Log2": Log2,
    "jijmodeling.expression.prod.ProdOperator": ProdOperator,
    "jijmodeling.expression.sum.SumOperator": SumOperator,
    "jijmodeling.expression.variables.deci_vars.Binary": Binary,
    "jijmodeling.expression.variables.deci_vars.LogEncInteger": Integer,
    "jijmodeling.expression.condition.NoneCondition": NoneCondition,
    "jijmodeling.expression.condition.AndOperator": AndOperator,
    "jijmodeling.expression.condition.OrOperator": OrOperator,
    "jijmodeling.expression.condition.XorOperator": XorOperator,
    "jijmodeling.expression.condition.Equal": Equal,
    "jijmodeling.expression.condition.LessEqual": LessThan,
    "jijmodeling.expression.condition.LessThanEqual": LessThanEqual,
    "jijmodeling.expression.constraint.Constraint": Constraint,
    "jijmodeling.expression.constraint.Penalty": Penalty,
}


def from_0_10_0_serializable(serializable: dict) -> Problem:
    if not serializable["version"] == "0.10.0":
        raise ValueError(
            f"In 'from_0_10_0_serializable', support only 0.10.0, not {serializable['version']}."
        )

    object_schema = serializable["object"]
    if not object_schema["class"] == "jijmodeling.problem.Problem":
        raise ValueError(
            f"{object_schema['class']} is not supported in 'from_0_10_0_serializable'."
        )

    attributes = object_schema["attributes"]
    name = attributes["name"]
    _kind_map = {"Minimum": ProblemSense.MINIMUM, "Maximum": ProblemSense.MAXIMUM}
    kind = _kind_map[attributes["kind"]]
    objective = _class_0100_from_serializable(attributes["objective"])
    constraints = [
        _class_0100_from_serializable(c) for c in attributes["constraints"].values()
    ]
    penalties = [
        _class_0100_from_serializable(c) for c in attributes["penalties"].values()
    ]

    problem = Problem(name, sense=kind)
    problem += objective
    for c in constraints:
        problem += c
    for p in penalties:
        problem += p

    return problem


def old_0_10_0_to_new_from_serializable(serializable: dict) -> Expression:
    """Deserialize from old schema to new JijModeling Expression."""
    object_schema = serializable["object"]
    return _class_0100_from_serializable(object_schema)


def _0100_from_serializable(object_schema: dict | int | float | None):
    if not isinstance(object_schema, dict):
        return object_schema
    if "class" in object_schema:
        return _class_0100_from_serializable(object_schema)
    elif "iteratable" in object_schema:
        return _iteratable_0100_from_serializable(object_schema)
    else:
        raise ValueError(
            f"'{object_schema.keys()}' is not supported in 0_10_0 deserializer."
        )


def _iteratable_0100_from_serializable(object_schema: dict):
    value = [_0100_from_serializable(v) for v in object_schema["value"]]
    if object_schema["iteratable"] == "tuple":
        return tuple(value)
    else:
        return value


def _class_0100_from_serializable(object_schema: dict):
    jm_cls = _OLD_NAME_TO_CLASS[object_schema["class"]]
    attributes = object_schema["attributes"]

    attr_values = {k: _0100_from_serializable(v) for k, v in attributes.items()}

    return jm_cls(**attr_values)
