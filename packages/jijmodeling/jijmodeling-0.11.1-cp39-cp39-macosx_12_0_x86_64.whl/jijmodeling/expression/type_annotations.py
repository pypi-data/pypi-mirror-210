from __future__ import annotations

import typing as tp

from jijmodeling.expression.expression import BinaryOperator, Expression, Number
from jijmodeling.expression.mathfunc import UnaryOperator
from jijmodeling.expression.variables.placeholders import ArrayShape, Placeholder
from jijmodeling.expression.variables.variable import (
    Element,
    Range,
    Subscripts,
    Variable,
)

# Type of subscript element
SubscriptElementType = (
    Expression  # tp.TypeVar("SubscriptElementType", bound=Expression)
)
# User Input type for subscript element
SubscriptElemInputType = tp.Union[slice, SubscriptElementType, int]

# Type of shape element
# tp.TypeVar("ShapeElementType", bound=Expression)
ShapeElementType = Expression
# User input type for shape element
ShapeElemInputType = tp.Union[ShapeElementType, int, None]

ElementParentType = tp.Union[Range, Variable, Subscripts]


NumericInt = int
ExprOrNum = tp.Union[Expression, int, float]

IntExpr = tp.Union[Expression, int]


ElementSetType = tp.Union[Range, Variable, Subscripts]


Operator = tp.Union[BinaryOperator, UnaryOperator]

StrictShapeElemType = tp.Union[
    Number,
    Placeholder,
    Operator,
    ArrayShape,
]
RangeBoundType = tp.TypeVar("RangeBoundType", bound=Expression)
SumIndexType = tp.TypeVar("SumIndexType", bound=Element)
OperandType = tp.TypeVar("OperandType", bound=Expression)
