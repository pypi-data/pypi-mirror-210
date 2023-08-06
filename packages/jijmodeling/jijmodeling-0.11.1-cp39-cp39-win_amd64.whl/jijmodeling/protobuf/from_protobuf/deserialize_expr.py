from __future__ import annotations

import struct

from dataclasses import dataclass
from typing import Union

import jijmodeling_schema as pb

from ulid import ULID

from jijmodeling.expression.condition import (
    AndOperator,
    CompareCondition,
    ConditionOperator,
    Equal,
    LessThan,
    LessThanEqual,
    NotEqual,
    OrOperator,
    XorOperator,
)
from jijmodeling.expression.expression import (
    Add,
    BinaryOperator,
    DataType,
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
    Max,
    Min,
    UnaryOperator,
)
from jijmodeling.expression.prod import ProdOperator
from jijmodeling.expression.sum import ReductionOperator, SumOperator
from jijmodeling.expression.variables.deci_vars import Binary, DecisionVariable, Integer
from jijmodeling.expression.variables.placeholders import ArrayShape, Placeholder
from jijmodeling.expression.variables.variable import Element, Range, Subscripts


def deserialize_expr(
    message: pb.Expression,
) -> Expression:
    """
    Convert a message object to a `Expression` object.

    Args:
        expression (pb.Expression): a `Expression` message

    Raises:
        RuntimeError: the error occurs if the massage cannot be converted to an object that is a subclass of the `Expression` class

    Returns:
        Expression: an instance object that is a subclass of the `Expression` class
    """
    deserializer = ProtobufDeserializer(message.expr_node_map)
    root = message.expr_node_map[message.id]
    return deserializer.deserialize_expr_kind(root)


@dataclass
class ProtobufDeserializer:
    node_map: dict

    def deserialize_number_lit(self, message: pb.NumberLit) -> Number:
        # Check the type that the number literal object has.
        # Case: integer
        if message.type == pb.NumberLitType.INTEGER:
            # Set the value type to `FLOAT`.
            dtype = DataType.INT
            # Set the integer value.
            value = struct.unpack(
                ">q",
                message.value.to_bytes(length=struct.calcsize(">q"), byteorder="big"),
            )[0]
        # Case: float
        elif message.type == pb.NumberLitType.FLOAT:
            # Set the value type to `FLOAT`.
            dtype = DataType.FLOAT
            # Convert the bits to a float value.
            value = struct.unpack(
                ">d",
                message.value.to_bytes(length=struct.calcsize(">d"), byteorder="big"),
            )[0]

        return Number(value=value, dtype=dtype, uuid=str(ULID()))

    def deserialize_placeholder(self, message: pb.Placeholder) -> Placeholder:
        return Placeholder(label=message.name, dim=message.ndim, uuid=str(ULID()))

    def deserialize_element(self, message: pb.Element) -> Element:
        belong_to = pb.betterproto.which_one_of(message, "belong_to")[1]
        if type(belong_to) is pb.ElementRange:
            start = self.deserialize_expr_kind(self.node_map[belong_to.start_id])
            end = self.deserialize_expr_kind(self.node_map[belong_to.end_id])
            return Element(
                label=message.name, parent=Range(start, end), uuid=str(ULID())
            )
        elif type(belong_to) is pb.ElementArray:
            array = self.deserialize_expr_kind(self.node_map[belong_to.array_id])
            return Element(label=message.name, parent=array, uuid=str(ULID()))
        else:
            raise ValueError(
                f"fail to deserialize the {type(belong_to)} message as a parent of the Element."
            )

    def deserialize_subscript(self, message: pb.Subscript) -> Subscripts:
        subscripted = self.deserialize_expr_kind(
            self.node_map[message.subscripted_variable_id]
        )
        subscripts = []
        for subscript_id in message.subscript_id_list:
            subscripts.append(self.deserialize_expr_kind(self.node_map[subscript_id]))
        return Subscripts(variable=subscripted, subscripts=subscripts, uuid=str(ULID()))

    def deserialize_array_length(self, message: pb.ArrayLength) -> ArrayShape:
        array = self.deserialize_expr_kind(self.node_map[message.array_id])
        return ArrayShape(array=array, dimension=message.axis, uuid=str(ULID()))

    def deserialize_decision_var(self, message: pb.DecisionVar) -> DecisionVariable:
        # NOTE: jijmodeling does not support for dynamic shape.
        #       So, the shape of the decision variable is created from the `dim` field.
        dummy_shape = tuple([10] * message.ndim)  # `10` is a dummy value.
        if message.type == pb.DecisionVarType.BINARY:
            return Binary(label=message.name, shape=dummy_shape, uuid=str(ULID()))
        elif message.type == pb.DecisionVarType.INTEGER:
            # Deserialize the lower bound.
            lower_bound = self.deserialize_expr_kind(
                self.node_map[message.lower_bound_id]
            )
            if isinstance(lower_bound, Placeholder) and lower_bound.dim != 0:
                lower_bound = Placeholder(
                    label=lower_bound.label, shape=dummy_shape, uuid=str(ULID())
                )
            # Deserialize the upper bound.
            upper_bound = self.deserialize_expr_kind(
                self.node_map[message.upper_bound_id]
            )
            if isinstance(upper_bound, Placeholder) and upper_bound.dim != 0:
                upper_bound = Placeholder(
                    label=upper_bound.label, shape=dummy_shape, uuid=str(ULID())
                )

            return Integer(
                label=message.name,
                shape=dummy_shape,
                lower=lower_bound,
                upper=upper_bound,
                uuid=str(ULID()),
            )

    def deserialize_unary_op(self, message: pb.UnaryOp) -> UnaryOperator:
        # Deserialize the operand.
        operand = self.deserialize_expr_kind(self.node_map[message.operand_id])

        if message.kind == pb.UnaryOpKind.ABS:
            return AbsoluteValue(operand, uuid=str(ULID()))
        elif message.kind == pb.UnaryOpKind.CEIL:
            return Ceil(operand, uuid=str(ULID()))
        elif message.kind == pb.UnaryOpKind.FLOOR:
            return Floor(operand, uuid=str(ULID()))
        elif message.kind == pb.UnaryOpKind.LOG_2:
            return Log2(operand, uuid=str(ULID()))
        else:
            raise ValueError(
                f"fail to deserialize the {message.kind} message as a UnaryOperator."
            )

    def deserialize_binary_op(
        self, message: pb.BinaryOp
    ) -> Union[BinaryOperator, CompareCondition]:
        # Deserialize the left operand.
        left = self.deserialize_expr_kind(self.node_map[message.left_id])
        # Deserialize the right operand.
        right = self.deserialize_expr_kind(self.node_map[message.right_id])

        if message.kind == pb.BinaryOpKind.POW:
            return Power(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.MOD:
            return Mod(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.MIN:
            return Min(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.MAX:
            return Max(left, right, uuid=str(ULID()))
        # Comparison operators.
        elif message.kind == pb.BinaryOpKind.EQ:
            return Equal(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.NOT_EQ:
            return NotEqual(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.LESS_THAN:
            return LessThan(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.LESS_THAN_EQ:
            return LessThanEqual(left, right, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.GREATER_THAN:
            return LessThan(right, left, uuid=str(ULID()))
        elif message.kind == pb.BinaryOpKind.GREATER_THAN_EQ:
            return LessThanEqual(right, left, uuid=str(ULID()))

    def deserialize_commutative_op(
        self, message: pb.CommutativeOp
    ) -> Union[BinaryOperator, ConditionOperator]:
        # Deserialize the operands.
        operands = []
        for operand_id in message.term_id_list:
            operands.append(self.deserialize_expr_kind(self.node_map[operand_id]))

        if message.kind == pb.CommutativeOpKind.ADD:
            return Add(*operands, uuid=str(ULID()))
        elif message.kind == pb.CommutativeOpKind.MUL:
            return Mul(*operands, uuid=str(ULID()))
        elif message.kind == pb.CommutativeOpKind.AND:
            return AndOperator(*operands, uuid=str(ULID()))
        elif message.kind == pb.CommutativeOpKind.OR:
            return OrOperator(*operands, uuid=str(ULID()))
        elif message.kind == pb.CommutativeOpKind.XOR:
            return XorOperator(*operands, uuid=str(ULID()))

    def deserialize_recution_op(self, message: pb.ReductionOp) -> ReductionOperator:
        # Deserialize the index.
        index = self.deserialize_expr_kind(self.node_map[message.index_id])

        # Deserialize the condition of the index.
        condition = (
            None
            if message.index_condition_id == ""
            else self.deserialize_expr_kind(self.node_map[message.index_condition_id])
        )

        # Deserialize the operand.
        operand = self.deserialize_expr_kind(self.node_map[message.operand_id])

        if message.kind == pb.ReductionOpKind.SUM:
            return SumOperator(index, operand, condition, uuid=str(ULID()))
        elif message.kind == pb.ReductionOpKind.PROD:
            return ProdOperator(index, operand, condition, uuid=str(ULID()))

    def deserialize_expr_kind(self, message: pb.ExpressionKind) -> Expression:
        expr_kind = pb.betterproto.which_one_of(message, "kind")[1]
        if type(expr_kind) is pb.NumberLit:
            return self.deserialize_number_lit(expr_kind)
        elif type(expr_kind) is pb.Placeholder:
            return self.deserialize_placeholder(expr_kind)
        elif type(expr_kind) is pb.Element:
            return self.deserialize_element(expr_kind)
        elif type(expr_kind) is pb.Subscript:
            return self.deserialize_subscript(expr_kind)
        elif type(expr_kind) is pb.ArrayLength:
            return self.deserialize_array_length(expr_kind)
        elif type(expr_kind) is pb.DecisionVar:
            return self.deserialize_decision_var(expr_kind)
        elif type(expr_kind) is pb.UnaryOp:
            return self.deserialize_unary_op(expr_kind)
        elif type(expr_kind) is pb.BinaryOp:
            return self.deserialize_binary_op(expr_kind)
        elif type(expr_kind) is pb.CommutativeOp:
            return self.deserialize_commutative_op(expr_kind)
        elif type(expr_kind) is pb.ReductionOp:
            return self.deserialize_recution_op(expr_kind)
        else:
            raise ValueError(
                f"cannot convert the {expr_kind.__class__.__name__} message into the object according to JijModeling.Expression"
            )
