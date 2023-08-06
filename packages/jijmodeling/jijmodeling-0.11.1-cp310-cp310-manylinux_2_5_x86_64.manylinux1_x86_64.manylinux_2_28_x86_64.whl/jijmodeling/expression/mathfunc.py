from __future__ import annotations

import abc as _abc
import builtins as _builtins
import numbers as _numbers
import typing as tp

from abc import abstractmethod

import numpy as np
import typeguard as _typeguard

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.expression as _expression


class UnaryOperator(_expression.Expression, metaclass=_abc.ABCMeta):
    """
    Binary Operator class represents each operation (ex. +,*,&,...) on `_expression.Expression`.
    """

    _mark = " "

    def __init__(
        self,
        operand: tp.Union[_expression.Expression, _expression.NumericValue],
        uuid: tp.Optional[str] = None,
    ):
        super().__init__()

        _typeguard.check_type(
            operand,
            tp.Union[_expression.Expression, _expression.NumericValue],
        )

        # convert int float to Number
        self._operand: _expression.Expression = (
            operand
            if isinstance(operand, _expression.Expression)
            else _expression.Number(operand)
        )

        import jijmodeling.utils.utils as _utils

        _utils.validate_value("operand.is_operatable()", self._operand.is_operatable())

        import jijmodeling.expression.extract as _extract

        if _extract.has_decivar(self._operand):
            raise _exceptions.CannotContainDecisionVarError(
                "An unary operator operand cannot contain a decision variable."
            )

        if uuid is not None:
            self._uuid = uuid

    @property
    def operand(self) -> _expression.Expression:
        return self._operand

    @classmethod
    @abstractmethod
    def operation(
        cls: tp.Type[UnaryOperator], operand: _expression.NumericValue
    ) -> _expression.NumericValue:
        """
        Execute operation.

        Examples:
            ```python
            Ceil.operation(4.3)
            # >>> 5
            Floor.operation(3.9)
            # >>> 3
            Log2.operation(4)
            # >>> 2.0
            ```
        """

    @classmethod
    def create(
        cls: tp.Type[UnaryOperator],
        operand: tp.Union[_expression.Expression, _expression.NumericValue],
    ) -> _expression.Expression:
        if isinstance(operand, (int, float, _numbers.Real)):
            return _expression.Number(cls.operation(operand))
        elif isinstance(operand, _expression.Number):
            return _expression.Number(cls.operation(operand.value))
        elif isinstance(operand, _expression.Expression):
            return cls(operand)
        else:
            raise _exceptions.ModelingError(
                "The operand of {} is support only number or_expression.Expression, not {}.".format(
                    cls.__name__, operand.__class__.__name__
                )
            )

    def is_operatable(self) -> bool:
        """
        Unary operator is operatable.

        Returns:
            bool: True
        """
        return True

    def children(self) -> tp.List[_expression.Expression]:
        return [self.operand]


class AbsoluteValue(UnaryOperator):
    """Absolute value operator."""

    def __repr__(self) -> str:
        return "|" + str(self.operand) + "|"

    @classmethod
    def operation(cls, operand: _expression.NumericValue) -> _expression.NumericValue:
        """operation of absolute value.
        Args:
            operand (_expression.NumericValue): operand of absolute value.

        Returns:
            _expression.NumericValue: absolute value of operand.
        """
        abs_value: _expression.NumericValue = np.abs(operand)
        return abs_value

    def _default_repr_latex_(self) -> str:
        return r"\left|" + self.operand._make_latex() + r"\right|"


class Max(_expression.BinaryOperator):
    """Max operator."""

    def __init__(
        self,
        left: _expression.Expression,
        right: _expression.Expression,
        uuid: tp.Optional[str] = None,
    ):
        super().__init__(left, right, uuid)

        import jijmodeling.expression.extract as _extract

        if _extract.has_decivar(self.left) or _extract.has_decivar(self.right):
            raise _exceptions.CannotContainDecisionVarError(
                "operands of Max function cannot contain a decision variable."
            )

    def __repr__(self) -> str:
        return "max(" + ",".join(map(str, [self.left, self.right])) + ")"

    @classmethod
    def operation(cls, left, right) -> tp.Any:
        """operation of max.

        Args:
            left (_expression.Expression): left operand of max.
            right (_expression.Expression): right operand of max.

        Returns:
            tp.Any: max value of left and right.
        """
        return _builtins.max(left, right)

    def _default_repr_latex_(self) -> str:
        left = self.left._make_latex()
        right = self.right._make_latex()
        return r"\max(" + f"{left}, {right})"


class Min(_expression.BinaryOperator):
    """Min operator."""

    def __init__(
        self,
        left: _expression.Expression,
        right: _expression.Expression,
        uuid: tp.Optional[str] = None,
    ):
        super().__init__(left, right, uuid)

        import jijmodeling.expression.extract as _extract

        if _extract.has_decivar(self.left) or _extract.has_decivar(self.right):
            raise _exceptions.CannotContainDecisionVarError(
                "operands of Max function cannot contain a decision variable."
            )

    def __repr__(self) -> str:
        return "min(" + ",".join(map(str, [self.left, self.right])) + ")"

    @classmethod
    def operation(cls, left, right) -> tp.Any:
        """operation of min.

        Args:
            left (_expression.Expression): left operand of min.
            right (_expression.Expression): right operand of min.

        Returns:
            tp.Any: min value of left and right.
        """
        return _builtins.min(left, right)

    def _default_repr_latex_(self) -> str:
        left = self.left._make_latex()
        right = self.right._make_latex()
        return r"\min(" + f"{left}, {right})"


class Ceil(UnaryOperator):
    """Ceil operator."""

    def __repr__(self):
        return "[" + str(self.operand) + "]"

    @classmethod
    def operation(cls, operand: _expression.NumericValue) -> _expression.NumericValue:
        ceil_value: _expression.NumericValue = np.ceil(operand)
        return ceil_value

    def _default_repr_latex_(self) -> str:
        term_str = (
            self.operand._make_latex()
            if isinstance(self.operand, _expression.Expression)
            else str(self.operand)
        )
        return r"\left\lceil " + term_str + r"\right\rceil"


class Floor(UnaryOperator):
    def __repr__(self) -> str:
        return "|_" + str(self.operand) + "_|"

    @classmethod
    def operation(cls, operand: _expression.NumericValue) -> _expression.NumericValue:
        floor_value: _expression.NumericValue = np.floor(operand)
        return floor_value

    def _default_repr_latex_(self) -> str:
        term_str = (
            self.operand._make_latex()
            if isinstance(self.operand, _expression.Expression)
            else str(self._operand)
        )
        return r"\left\lfloor " + term_str + r"\right\floor "


class Log2(UnaryOperator):
    def __repr__(self) -> str:
        return f"log2({str(self.operand)})"

    @classmethod
    def operation(cls, operand: _expression.NumericValue) -> tp.Any:
        return np.log2(operand)

    def _default_repr_latex_(self) -> str:
        return r"\log_2" + f"({self.operand._make_latex()})"


def abs(term) -> _expression.Expression:
    """Absolute function.
    Args:
        term (int | float | Expression): term of absolute value.
    Returns:
        Union[AbsoluteValue, Expression]: absolute value of term.
    """
    return AbsoluteValue.create(term)


def ceil(term) -> _expression.Expression:
    """Ceiling function.
    Args:
        term (int | float | Expression): term of ceiling function.

    Returns:
        Union[Ceil, Expression]: ceiling value of term.
    """
    return Ceil.create(term)


def floor(term) -> _expression.Expression:
    """Floor function.

    Args:
        term (int | float | Expression): term of floor function.

    Returns:
        Union[Floor, Expression]: floor value of term.
    """
    return Floor.create(term)


def log2(antilog) -> _expression.Expression:
    """
    Log function.

    Args:
        antilog (int | float |_expression.Expression): antilog

    $$\\log_{2}\\mathrm{antilog}$$


    Returns:
        : Log2 value
    """
    return Log2.create(antilog)


def max(left, right) -> _expression.Expression:
    """Max function.

    Args:
        left (int | float | _expression.Expression): left operand of max.
        right (int | float | _expression.Expression): right operand of max.

    Returns:
        Union[Max, Expression]: max value of left and right.
    """
    return Max.create(left, right)


def min(left, right) -> _expression.Expression:
    """Min function.

    Args:
        left (int | float | _expression.Expression): left operand of min.
        right (int | float | _expression.Expression): right operand of min.

    Returns:
        Union[Min, Expression]: min value of left and right.
    """
    return Min.create(left, right)
