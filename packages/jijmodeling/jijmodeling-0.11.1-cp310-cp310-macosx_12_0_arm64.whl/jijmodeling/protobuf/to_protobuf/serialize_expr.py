from __future__ import annotations

import struct

from dataclasses import dataclass
from typing import Union

import jijmodeling_schema as pb

from ulid import ULID

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
    DataType,
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
    Max,
    Min,
    UnaryOperator,
)
from jijmodeling.expression.prod import ProdOperator
from jijmodeling.expression.sum import ReductionOperator, SumOperator
from jijmodeling.expression.variables.deci_vars import Binary, Integer
from jijmodeling.expression.variables.jagged_array import JaggedArray
from jijmodeling.expression.variables.placeholders import ArrayShape, Placeholder
from jijmodeling.expression.variables.variable import Element, Range, Subscripts


def serialize_expr(expr: Union[Expression, Condition]) -> pb.Expression:
    """
    Convert a `Expression` instance object to an `Expression` message.

    Args:
        expr (Expression): an `Expression` instance object

    Raises:
        TypeError: the error occurs if the instance ofject cannot be converted to a protobuf object

    Returns:
        pb.Expression: a `Expression` message
    """
    serializer = ProtobufSerializer()
    serializer.serialize_expr(expr)

    # Create an empty `Expression` message.
    message = pb.Expression()

    message.id = serializer.root_id

    # Set the kind of nodes to `NumberLit`.
    message.expr_node_map = serializer.node_map

    # Serialize the `Expression` object into a bytes object.
    return message


@dataclass
class ProtobufSerializer:
    node_map: dict
    root_id: str

    def __init__(self):
        self.node_map = {}
        self.root_id = ""

    def add_expression_kind(self, kind: pb.ExpressionKind):
        # Create the id of the expression node.
        root_id = str(ULID())

        # Set the id as a root.
        self.root_id = root_id

        # Insert the id-kind pair into the node_map.
        self.node_map.update({root_id: kind})

    def make_element_message(self, element: Element) -> pb.Element:
        # Create an empty `Element` message.
        elt_msg = pb.Element()

        # Set the name of the element.
        elt_msg.name = element.label

        # Set the dimension of the element.
        elt_msg.ndim = element.dim

        # Serialize the parent of the element.
        if type(element.parent) is Range:
            # Serialize the start of the range.
            self.serialize_expr(element.parent.start)
            start_id = self.root_id
            # Serialize the end of the range.
            self.serialize_expr(element.parent.last)
            end_id = self.root_id
            # Set the range of the element.
            elt_msg.range = pb.ElementRange(start_id=start_id, end_id=end_id)
        else:
            self.serialize_expr(element.parent)
            elt_msg.array = pb.ElementArray(array_id=self.root_id)

        return elt_msg

    def serialize_number_lit(self, lit: Number):
        # Create an empty `NumberLit` message.
        lit_msg = pb.NumberLit()

        # Set the type of the value that the `Number` object has.
        # Case: int
        if lit.dtype == DataType.INT:
            lit_msg.type = pb.NumberLitType.INTEGER

            # Set the value that the `Number` object has.
            # Convert the value to the bytes object.
            lit_msg.value = int.from_bytes(struct.pack(">q", lit.value), "big")
        # Case: float
        elif lit.dtype == DataType.FLOAT:
            lit_msg.type = pb.NumberLitType.FLOAT

            # Set the value that the `Number` object has.
            # Convert the value to the bytes object.
            lit_msg.value = int.from_bytes(struct.pack(">d", lit.value), "big")
        # Otherwise
        else:
            lit_msg.type = pb.NumberLitType.UNKNOWN

        self.add_expression_kind(pb.ExpressionKind(number_lit=lit_msg))

    def serialize_placeholder(self, ph: Placeholder):
        # Create an empty `Placeholder` message.
        ph_msg = pb.Placeholder()

        # Set the name of the placeholder.
        ph_msg.name = ph.label

        # Set the dimension of the placeholder.
        ph_msg.ndim = ph.dim

        self.add_expression_kind(pb.ExpressionKind(placeholder=ph_msg))

    def serialize_jagged_array(self, jagged_array: JaggedArray):
        # Create an empty `Placeholder` message.
        ph_msg = pb.Placeholder()

        # Set the name of the placeholder.
        ph_msg.name = jagged_array.label

        # Set the dimension of the placeholder.
        ph_msg.ndim = jagged_array.dim

        self.add_expression_kind(pb.ExpressionKind(placeholder=ph_msg))

    def serialize_element(self, element: Element):
        elt_msg = self.make_element_message(element)
        self.add_expression_kind(pb.ExpressionKind(element=elt_msg))

    def serialize_subscript(self, subscripted: Subscripts):
        # Create an empty `Subscript` message.
        subscript_msg = pb.Subscript()

        # Set the dimension of the subscripted variable.
        subscript_msg.ndim = subscripted.dim

        # Serialize the subscripted variable.
        self.serialize_expr(subscripted.variable)
        subscript_msg.subscripted_variable_id = self.root_id

        # Serialize the subscripts.
        for subscript in subscripted.subscripts:
            self.serialize_expr(subscript)
            subscript_msg.subscript_id_list.append(self.root_id)

        self.add_expression_kind(pb.ExpressionKind(subscript=subscript_msg))

    def serialize_array_shape(self, array_shape: ArrayShape):
        # Create an empty `ArrayLength` message.
        array_length_msg = pb.ArrayLength()

        # Serialize the array of the array length.
        self.serialize_expr(array_shape.array)
        array_length_msg.array_id = self.root_id

        # Set the axis of the array length.
        array_length_msg.axis = array_shape.dimension

        self.add_expression_kind(pb.ExpressionKind(array_length=array_length_msg))

    def serialize_binary_var(self, var: Binary):
        # Create an empty `DecisionVar` message.
        var_msg = pb.DecisionVar()

        # Set the name of the binary variable.
        var_msg.name = var.label

        # Set the dimension of the binary variable.
        var_msg.ndim = var.dim

        # Set the type to a binary variable.
        var_msg.type = pb.DecisionVarType.BINARY

        self.add_expression_kind(pb.ExpressionKind(decision_var=var_msg))

    def serialize_integer_var(self, var: Integer):
        # Create an empty `DecisionVar` message.
        var_msg = pb.DecisionVar()

        # Set the name of the integer variable.
        var_msg.name = var.label

        # Set the dimension of the integer variable.
        var_msg.ndim = var.dim

        # Set the type to an integer variable.
        var_msg.type = pb.DecisionVarType.INTEGER

        # Serialize the lower bound of the integer variable.
        self.serialize_expr(var.lower)
        var_msg.lower_bound_id = self.root_id

        # Serialize the upper bound of the integer variable.
        self.serialize_expr(var.upper)
        var_msg.upper_bound_id = self.root_id

        self.add_expression_kind(pb.ExpressionKind(decision_var=var_msg))

    def serialize_unary_op(self, op: UnaryOperator):
        # Create an empty `UnaryOp` message.
        op_msg = pb.UnaryOp()

        # Serialize the operand of the unary operation.
        self.serialize_expr(op.operand)
        op_msg.operand_id = self.root_id

        # Set the type of the unary operator.
        if type(op) is AbsoluteValue:
            op_msg.kind = pb.UnaryOpKind.ABS
        elif type(op) is Ceil:
            op_msg.kind = pb.UnaryOpKind.CEIL
        elif type(op) is Floor:
            op_msg.kind = pb.UnaryOpKind.FLOOR
        elif type(op) is Log2:
            op_msg.kind = pb.UnaryOpKind.LOG_2

        self.add_expression_kind(pb.ExpressionKind(unary_op=op_msg))

    def serialize_binary_op(self, op: BinaryOperator):
        if isinstance(op, (Add, Mul)):
            # Create an empty `CommutativeOp` message.
            op_msg = pb.CommutativeOp()

            # Serialize the left operand of the binary operation.
            self.serialize_expr(op.left)
            op_msg.term_id_list.append(self.root_id)

            # Serialize the right operand of the binary operation.
            self.serialize_expr(op.right)
            op_msg.term_id_list.append(self.root_id)

            # Set the type of the commutative opeator.
            if type(op) is Add:
                op_msg.kind = pb.CommutativeOpKind.ADD
            elif type(op) is Mul:
                op_msg.kind = pb.CommutativeOpKind.MUL

            self.add_expression_kind(pb.ExpressionKind(commutative_op=op_msg))

        elif isinstance(op, Div):
            left = op.left
            right = op.right
            # left / right = left * right^-1
            expr = left * Power(right, Number(-1))
            self.serialize_expr(expr)

        else:
            # Create an empty `BinaryOp` message.
            op_msg = pb.BinaryOp()

            # Serialize the left operand of the binary operation.
            self.serialize_expr(op.left)
            op_msg.left_id = self.root_id

            # Serialize the right operand of the binary operation.
            self.serialize_expr(op.right)
            op_msg.right_id = self.root_id

            # Set the type of the binary operation.
            if type(op) is Power:
                op_msg.kind = pb.BinaryOpKind.POW
            elif type(op) is Mod:
                op_msg.kind = pb.BinaryOpKind.MOD
            elif type(op) is Min:
                op_msg.kind = pb.BinaryOpKind.MIN
            elif type(op) is Max:
                op_msg.kind = pb.BinaryOpKind.MAX

            self.add_expression_kind(pb.ExpressionKind(binary_op=op_msg))

    def serialize_comparison_op(self, op: CompareCondition):
        # Create an empty `BinaryOp` message.
        op_msg = pb.BinaryOp()

        # Serialize the left operand.
        self.serialize_expr(op.left)
        op_msg.left_id = self.root_id

        # Serialize the right operand.
        self.serialize_expr(op.right)
        op_msg.right_id = self.root_id

        # Set the type of the comparison operation.
        if type(op) is Equal:
            op_msg.kind = pb.BinaryOpKind.EQ
        elif type(op) is NotEqual:
            op_msg.kind = pb.BinaryOpKind.NOT_EQ
        elif type(op) is LessThan:
            op_msg.kind = pb.BinaryOpKind.LESS_THAN
        elif type(op) is LessThanEqual:
            op_msg.kind = pb.BinaryOpKind.LESS_THAN_EQ

        self.add_expression_kind(pb.ExpressionKind(binary_op=op_msg))

    def serialize_logical_op(self, op: ConditionOperator):
        # Create an empty `CommutativeOp` message.
        op_msg = pb.CommutativeOp()

        # Serialize the left operand of the binary operation.
        self.serialize_expr(op.left)
        op_msg.term_id_list.append(self.root_id)

        # Serialize the right operand of the binary operation.
        self.serialize_expr(op.right)
        op_msg.term_id_list.append(self.root_id)

        # Set the type of the commutative opeator.
        if type(op) is AndOperator:
            op_msg.kind = pb.CommutativeOpKind.AND
        elif type(op) is OrOperator:
            op_msg.kind = pb.CommutativeOpKind.OR
        elif type(op) is XorOperator:
            op_msg.kind = pb.CommutativeOpKind.XOR

        self.add_expression_kind(pb.ExpressionKind(commutative_op=op_msg))

    def serialize_reduction(self, op: ReductionOperator):
        # Create an empty `Reduction` message.
        op_msg = pb.ReductionOp()

        # Set the type of the reduction operator.
        if type(op) is SumOperator:
            op_msg.kind = pb.ReductionOpKind.SUM
        elif type(op) is ProdOperator:
            op_msg.kind = pb.ReductionOpKind.PROD

        # Serialize the index.
        self.serialize_element(op.sum_index)
        op_msg.index_id = self.root_id

        # Serialize the condition for the index if it exists.
        if type(op.condition) is not NoneCondition:
            self.serialize_expr(op.condition)
            op_msg.index_condition_id = self.root_id

        # Serialize the operand of the reduction operator.
        self.serialize_expr(op.operand)
        op_msg.operand_id = self.root_id

        self.add_expression_kind(pb.ExpressionKind(reduction_op=op_msg))

    def serialize_expr(self, expr: Union[Expression, Condition]):
        if type(expr) is Number:
            self.serialize_number_lit(expr)
        elif type(expr) is Placeholder:
            self.serialize_placeholder(expr)
        elif type(expr) is JaggedArray:
            self.serialize_jagged_array(expr)
        elif type(expr) is Element:
            self.serialize_element(expr)
        elif type(expr) is ArrayShape:
            self.serialize_array_shape(expr)
        elif type(expr) is Subscripts:
            self.serialize_subscript(expr)
        elif type(expr) is Binary:
            self.serialize_binary_var(expr)
        elif type(expr) is Integer:
            self.serialize_integer_var(expr)
        elif isinstance(expr, UnaryOperator):
            self.serialize_unary_op(expr)
        elif isinstance(expr, BinaryOperator):
            self.serialize_binary_op(expr)
        elif isinstance(expr, CompareCondition):
            self.serialize_comparison_op(expr)
        elif isinstance(expr, ConditionOperator):
            self.serialize_logical_op(expr)
        elif isinstance(expr, ReductionOperator):
            self.serialize_reduction(expr)
        else:
            raise TypeError(
                f"{expr.__class__.__name__} is not supported for protobuf serialization."
            )
