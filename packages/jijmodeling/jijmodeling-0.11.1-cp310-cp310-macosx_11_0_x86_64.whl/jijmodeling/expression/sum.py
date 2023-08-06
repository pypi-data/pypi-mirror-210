from __future__ import annotations

import typing as tp

import typeguard as _typeguard

from typeguard import typechecked

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.condition as _conditions
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.extract as _extract

# type validation
import jijmodeling.expression.type_annotations as _type_annotations
import jijmodeling.expression.variables.variable as _variable
import jijmodeling.utils.utils as _utils


class ReductionOperator(_expression.Expression):
    """Super class of reduction operators.
    Subclass examples: SumOperator, ProdOperator
    """

    def __init__(
        self,
        sum_index: _variable.Element,
        operand: _expression.Expression,
        condition: tp.Optional[_conditions.Condition] = None,
        uuid: tp.Optional[str] = None,
    ) -> None:
        super().__init__(uuid=uuid)

        self._sum_index = sum_index
        self._operand = operand
        self._condition: _conditions.Condition = (
            _conditions.NoneCondition() if condition is None else condition
        )
        if uuid is not None:
            self._uuid = uuid

        if _extract.condition_has_decivar(self._condition):
            raise _exceptions.CannotContainDecisionVarError(
                "condition for sum index cannot contain decision variable."
            )

        ConditionType = tp.Optional[_conditions.Condition]
        _typeguard.check_type(self._sum_index, _type_annotations.SumIndexType)
        _typeguard.check_type(self._operand, _type_annotations.OperandType)
        _typeguard.check_type(self._condition, ConditionType)

    @property
    def sum_index(self) -> _variable.Element:
        """Summation index."""
        return self._sum_index

    @property
    def operand(self) -> _expression.Expression:
        """Summation operand."""
        return self._operand

    @property
    def condition(self) -> _conditions.Condition:
        """Summation condition."""
        return self._condition

    def children(self) -> list:
        """[sum_index, operand, condition]."""
        return [self._sum_index, self._operand] + self.condition.expressions()

    def is_operatable(self) -> bool:
        return True

    def __repr__(self) -> str:
        sum_index = ""
        if isinstance(self.sum_index.parent, _variable.Range):
            sum_index = "{" + "{}={}".format(
                self.sum_index, self.sum_index.parent.start
            )
            sum_index = sum_index + "}"
            sum_index = sum_index + "^{" + str(self.sum_index.parent.last) + "}"
        else:
            sum_index = "{" + f"{self.sum_index} in {self.sum_index.parent}"
            sum_index = sum_index + "}"

        return "Sum_" + sum_index + "(" + str(self.operand) + ")"


class SumOperator(ReductionOperator):
    """
    Class that represents the sum.

    Example:
        Create $`\\sum_{i=0}^n d_i x_i`$

        ```python
        from jijmodeling import Placeholder, Binary, SumOperator
        from jijmodeling import Element
        d = Placeholder('d', dim=1)
        n = d.shape[0]
        x = Binary('x', shape=n)
        i = Element("i", n)
        SumOperator(sum_index=i, operand=d[i]*x[i], condition=None)
        # Σ_{i}(d[i]x[i])
        ```
    """


INDEXWITHCOND = tp.Union[
    _variable.Element, tp.Tuple[_variable.Element, _conditions.Condition]
]


def Sum(
    indices: tp.Union[INDEXWITHCOND, tp.List[INDEXWITHCOND]],
    term: _expression.Expression,
) -> SumOperator:
    """
    Sum function.

    Args:
        indices: summation index dict or list of index.
        term (Expression): operand of summation

    Returns:
        SumOperator: SumOperator object.

    Example:
        Create $`\\sum_{i=0}^n d_i x_i`$

        ```python
        import jijmodeling as jm
        d = jm.Placeholder('d', dim=1)
        n = d.shape[0]
        x = jm.Binary('x', shape=n)
        i = jm.Element('i', n)
        jm.Sum(i, d[i]*x[i])
        # Σ_{i}(d[i]x[i])
        ```

        Create $`\\sum_{i}\\sum_j d_{ij}x_i x_j`$

        ```python
        import jijmodeling as jm
        d = jm.Placeholder('d', dim = 2)
        n = d.shape[0]
        x = jm.Binary('x', shape=n)
        i = jm.Element('i', n)
        j = jm.Element('j', n)
        jm.Sum([i, j], d[i, j]*x[i]*x[j])
        ```

        Conditional sum
        ```python
        import jijmodeling as jm
        d = jm.Placeholder('d', dim = 2)
        n = d.shape[0]
        i, j = jm.Element("i", n), jm.Element("j", n)
        x = jm.Binary('x', shape=n)
        jm.Sum([i, (j, i < j)], d[i, j]*x[i]*x[j])
        ```
    """

    # convert indices and condition to list-type object
    # ex. i -> [i]
    indices_list = indices if isinstance(indices, list) else [indices]  # type: ignore

    # element type from users
    IndexType = tp.Union[
        _variable.Element,
        tp.Tuple[_variable.Element, tp.Optional[_conditions.Condition]],
    ]

    @typechecked
    def convert_to_element(
        index: IndexType,
    ) -> tp.Tuple[_variable.Element, tp.Optional[_conditions.Condition]]:
        if isinstance(index, tuple):  # Tuple[ElementType, Optional[Condition]]
            elem, cond = index
            return (elem, cond)
        else:  # ElementType
            return (index, None)

    elems_and_conds: tp.List[
        tp.Tuple[_variable.Element, tp.Optional[_conditions.Condition]]
    ] = [convert_to_element(index) for index in indices_list]
    elements = [elem for elem, _ in elems_and_conds]
    condition_list = [cond for _, cond in elems_and_conds]

    # list length validation
    _utils.validate_value("len(indices) > 0", len(elements) > 0)
    _utils.validate_value("len(condition_list) > 0", len(condition_list) > 0)
    _utils.validate_value(
        "len(indices_list)  == len(condition_list)",
        len(indices_list) == len(condition_list),
    )
    sum_term = term
    for sum_index, cond in zip(elements[::-1], condition_list[::-1]):
        sum_term = SumOperator(
            sum_index=sum_index,
            operand=sum_term,
            condition=cond if cond is not None else _conditions.NoneCondition(),
        )
    return sum_term  # type: ignore
