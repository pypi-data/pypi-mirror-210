from __future__ import annotations

import abc as _abc
import typing as tp
import uuid

from abc import abstractmethod

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.serializable as _serializable


class Condition(metaclass=_serializable.Serializable):
    """Super class for Conditions."""

    def __init__(self) -> None:
        self._uuid = uuid.uuid4().hex

    def __and__(self, other):
        return AndOperator(self, other)

    def __xor__(self, other):
        return XorOperator(self, other)

    def __or__(self, other):
        return OrOperator(self, other)

    def __bool__(self):
        raise TypeError(
            "Cannot convert jm.Condition to bool to avoid unexpected bahavior. Consider using `jm.expr_same` instead in order to compare `jm.Condition` objects."
        )

    @abstractmethod
    def expressions(self) -> tp.List[_expression.Expression]:
        pass

    @property
    def uuid(self) -> str:
        return self._uuid


class NoneCondition(Condition):
    """NoneCondition is a special condition that always returns None."""

    def expressions(self) -> tp.List[_expression.Expression]:
        return []

    @classmethod
    def operation(cls) -> bool:
        return True

    def _make_latex(self) -> str:
        """
        Outputs a latex representation.

        If `self._latex_repr` is not None, it
        will take precedence. If you want to get the latex representation of
        child objects in `_default_repr_latex_` of each class, use the method.

        Returns:
            str: latex representation.
        """
        return ""


class CompareCondition(Condition, metaclass=_abc.ABCMeta):
    mark = ""

    def __init__(
        self,
        left: tp.Union[_expression.Expression, _expression.NumericValue],
        right: tp.Union[_expression.Expression, _expression.NumericValue],
        uuid: tp.Optional[str] = None,
    ) -> None:
        _left: _expression.Expression = (
            left
            if isinstance(left, _expression.Expression)
            else _expression.Number(left)
        )
        _right: _expression.Expression = (
            right
            if isinstance(right, _expression.Expression)
            else _expression.Number(right)
        )

        super().__init__()
        if not _left.is_operatable():
            raise _exceptions.ModelingError(f"{_left} is not operatable.")
        if not _right.is_operatable():
            raise _exceptions.ModelingError(f"{_right} is not operatable.")

        self._left = _left
        self._right = _right
        # Set uuid
        if uuid is not None:
            self._uuid = uuid

    def __repr__(self) -> str:
        return str(self.left) + self.mark + str(self.right)

    def _make_latex(self) -> str:
        """
        Outputs a latex representation.

        If `self._latex_repr` is not None, it
        will take precedence. If you want to get the latex representation of
        child objects in `_default_repr_latex_` of each class, use the method.

        Returns:
            str: latex representation.
        """
        latex_str = r"{} {} {}".format(
            self.left._make_latex(), self.mark, self.right._make_latex()
        )
        return latex_str

    def _repr_latex_(self) -> str:
        """
        Latex representation for Jupyter notebook.

        Returns:
            str: latex string
        """
        return f"${self._make_latex()}$"

    @property
    def left(self) -> _expression.Expression:
        return self._left

    @property
    def right(self) -> _expression.Expression:
        return self._right

    def expressions(self) -> tp.List[_expression.Expression]:
        return [self.left, self.right]

    @classmethod
    @abstractmethod
    def operation(cls, left, right) -> bool:
        pass


class Equal(CompareCondition):
    """Equal condition."""

    mark = "="

    def __init__(
        self,
        left: tp.Union[_expression.Expression, _expression.NumericValue],
        right: tp.Union[_expression.Expression, _expression.NumericValue],
        uuid: tp.Optional[str] = None,
    ) -> None:
        _left = (
            left
            if isinstance(left, _expression.Expression)
            else _expression.Number(left)
        )
        _right = (
            right
            if isinstance(right, _expression.Expression)
            else _expression.Number(right)
        )
        super().__init__(_left, _right, uuid)

    @classmethod
    def operation(cls, left: tp.Any, right: tp.Any) -> bool:
        equal: bool = left == right
        return equal


class NotEqual(CompareCondition):
    """NotEqual condition."""

    mark = "!="

    def __init__(
        self,
        left: tp.Union[_expression.Expression, _expression.NumericValue],
        right: tp.Union[_expression.Expression, _expression.NumericValue],
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(left, right, uuid)

    def _make_latex(self) -> str:
        """
        Outputs a latex representation.

        If `self._latex_repr` is not None, it
        will take precedence. If you want to get the latex representation of
        child objects in `_default_repr_latex_` of each class, use the method.

        Returns:
            str: latex representation.
        """
        latex_str = r"{} \neq {}".format(
            self.left._make_latex(), self.right._make_latex()
        )
        return latex_str

    @classmethod
    def operation(cls, left, right) -> bool:
        not_eq: bool = left != right
        return not_eq


class LessThan(CompareCondition):
    mark = "<"

    def __init__(
        self,
        left: tp.Union[_expression.Expression, _expression.NumericValue],
        right: tp.Union[_expression.Expression, _expression.NumericValue],
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(left, right, uuid)

    @classmethod
    def operation(cls, left, right) -> bool:
        less_than: bool = left < right
        return less_than


class LessThanEqual(CompareCondition):
    mark = "<="

    def __init__(
        self,
        left: tp.Union[_expression.Expression, _expression.NumericValue],
        right: tp.Union[_expression.Expression, _expression.NumericValue],
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(left, right, uuid)

    def _make_latex(self) -> str:
        """
        Outputs a latex representation.

        If `self._latex_repr` is not None, it
        will take precedence. If you want to get the latex representation of
        child objects in `_default_repr_latex_` of each class, use the method.

        Returns:
            str: latex representation.
        """
        latex_str = r"{} \leq {}".format(
            self.left._make_latex(), self.right._make_latex()
        )
        return latex_str

    @classmethod
    def operation(cls, left, right) -> bool:
        less_than_eq: bool = left <= right
        return less_than_eq


def equal(left: _expression.Expression, right: _expression.Expression) -> Equal:
    """
    Creadion an Equality condition object (Equal).

    The equality operator `==` can also be used to generate an equality condition object.
    Args:
        left (Expression): left hand side expression
        right (Expression): right hand side expression

    Returns:
        Equal: left `==` right
    """
    return Equal(left, right)


def eq(left: _expression.Expression, right: _expression.Expression) -> Equal:
    """
    Creadion an Equality condition object (Equal).
    """
    return equal(left, right)


def neq(left: _expression.Expression, right: _expression.Expression) -> NotEqual:
    """
    Creadion a Non Equality condition object (NotEqual) The non equality.

    operator `!=` can also be used to generate a non equality condition object.

    Args:
        left (Expression): left hand side expression
        right (Expression): right hand side expression

    Returns:
        NotEqual: left `!=` right
    """
    return NotEqual(left, right)


class ConditionOperator(Condition, metaclass=_abc.ABCMeta):
    def __init__(
        self,
        left: Condition,
        right: Condition,
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__()
        self._left = left
        self._right = right
        # Set uuid
        if uuid is not None:
            self._uuid = uuid

    @property
    def left(self) -> Condition:
        return self._left

    @property
    def right(self) -> Condition:
        return self._right

    def expressions(self) -> tp.List[_expression.Expression]:
        return self.left.expressions() + self.right.expressions()

    @classmethod
    @abstractmethod
    def operation(cls, left: bool, right: bool) -> bool:
        pass


class AndOperator(ConditionOperator):
    def __init__(
        self,
        left: Condition,
        right: Condition,
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(left, right, uuid)

    @classmethod
    def operation(cls, left: bool, right: bool) -> bool:
        and_ope: bool = left & right
        return and_ope

    def __repr__(self) -> str:
        return "(" + str(self.left) + ") & (" + str(self.right) + ")"


class XorOperator(ConditionOperator):
    def __init__(
        self,
        left: Condition,
        right: Condition,
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(left, right, uuid)

    @classmethod
    def operation(cls, left, right) -> bool:
        xor: bool = left ^ right
        return xor

    def __repr__(self) -> str:
        return str(self.left) + " xor " + str(self.right)


class OrOperator(ConditionOperator):
    def __init__(
        self,
        left: Condition,
        right: Condition,
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(left, right, uuid)

    @classmethod
    def operation(cls, left, right) -> bool:
        or_bool: bool = left | right
        return or_bool

    def __repr__(self) -> str:
        return str(self.left) + " | " + str(self.right)
