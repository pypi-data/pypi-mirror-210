from __future__ import annotations

"""TYPE ANNOTATIONS.

Describe the types related to the data needed to change from JijModeling to another type, such as to_pyqubo or calc_value.
"""

import typing as tp

import numpy as np

from jijmodeling.expression.variables.deci_vars import DecisionVariable
from jijmodeling.expression.variables.placeholders import Placeholder

NumberValue = tp.Union[int, float]
TensorValue = tp.Union[NumberValue, np.ndarray]
ListValue = tp.List[NumberValue]
NonZeroIndices = tp.Tuple[tp.List[int], ...]
NonZeroValues = tp.Union[tp.List[tp.Union[int, float]], tp.Union[int, float]]
Shape = tp.Tuple[int, ...]
SparseSolution = tp.Tuple[
    NonZeroIndices,
    NonZeroValues,
    Shape,
]
DenseSolution = np.ndarray

ForallIndexType = tp.Dict[str, tp.List[tp.List[int]]]
ForallValuesType = tp.Dict[str, tp.List[float]]
ConstraintExpressionValuesType = tp.Dict[str, tp.Dict[tp.Tuple[int, ...], float]]


ForallIndexType = tp.Dict[str, tp.List[tp.List[int]]]
ForallValuesType = tp.Dict[str, tp.List[float]]
ConstraintExpressionValuesType = tp.Dict[str, tp.Dict[tp.Tuple[int, ...], float]]


VARIABLE_KEY = tp.Union[str, Placeholder]
# User interface for values of placeholder.
PH_VALUES_INTERFACE = tp.Dict[VARIABLE_KEY, tp.Union[TensorValue, ListValue]]
# type of value of placholders for inner handling.
PLACEHOLDER_VALUES = tp.Dict[Placeholder, tp.Union[TensorValue, ListValue]]

DECI_VALUES_INTEREFACE = tp.Dict[tp.Union[str, DecisionVariable], TensorValue]
DECISION_VALUES = tp.Dict[DecisionVariable, TensorValue]

# fixed variable
# ex. fix array element : {"x": {(0, 1, 2): 1}} means x[0, 1, 2] = 1
#     fix scalar variable: {"y": {(): 0}} means y = 0
FIXED_VARS_INTERFACE = tp.Dict[
    tp.Union[str, DecisionVariable],
    tp.Dict[tp.Tuple[int, ...], NumberValue],
]
FIXED_VARIABLES = tp.Dict[DecisionVariable, tp.Dict[tp.Tuple[int, ...], NumberValue]]
