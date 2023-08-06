from __future__ import annotations

import typing as typ
from typing import List, Optional, Tuple, Union

from typeguard import check_type, typechecked

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.condition as _condition
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.serializable as _serializable
import jijmodeling.expression.sum as _sum
import jijmodeling.expression.variables.variable as _variable
import jijmodeling.utils.deprecated as _deprecated


class Penalty(metaclass=_serializable.Serializable):
    """
    Penalty term without constraint.

    Incorporate it into the model as a penalty term. It is not evaluated
    as a constraint, so it is not used to determine if a solution is
    feasible. However, it is evaluated separately from the objective
    function. It is mainly used to include conditions that you want to
    treat as soft constraints as penalty terms. The penalty class can
    also be used when you would like to express the constraint as a
    penalty that you define, rather than one that is automatically
    changed by QUBO.
    """

    def __init__(
        self,
        label: str,
        penalty_term: _expression.Expression,
        forall: Union[
            _variable.Element,
            Tuple[_variable.Element, Optional[_condition.Condition]],
            List[
                Union[
                    _variable.Element,
                    Tuple[_variable.Element, Optional[_condition.Condition]],
                ]
            ],
        ] = [],
        with_multiplier: typ.Optional[bool] = None,
    ):
        """
        Initializes a Penalty object without constraint.

        Args:
            label (str): A unique identifier for the penalty term.
            penalty_term (_expression.Expression): The expression representing the penalty term.
            forall (tuple, optional): A list of elements and optional conditions that the penalty term applies to. Default is an empty list.
            with_multiplier (typ.Optional[bool], deprecated): A flag indicating whether to use a multiplier in the penalty term. This argument is deprecated and will be removed in the next version. Default is None.

        Example:
            ```python
            import jijmodeling as jm
            n = jm.Placeholder('n')
            x = jm.Binary('x', shape=n)
            pe = jm.Penalty('p', (x[:]-1)**2) # one-hot constraint
            ```
        """
        self._label = label
        self._penalty_term = penalty_term

        # deprecated
        warning_msg = "This optional argument will be removed in the next version."
        _deprecated.is_deprecated(
            "with_multiplier", with_multiplier, additional_msg=warning_msg
        )
        if with_multiplier is None:
            self._with_multiplier = True
        else:
            self._with_multiplier = with_multiplier

        # convert forall to list-type object
        forall_list = forall if isinstance(forall, list) else [forall]
        # element type from users
        IndexType = Union[
            _variable.Element, Tuple[_variable.Element, Optional[_condition.Condition]]
        ]

        @typechecked
        def convert_to_element(
            index: IndexType,
        ) -> Tuple[_variable.Element, _condition.Condition]:
            if isinstance(index, tuple):  # Tuple[ElementType, Condition]
                elem, cond = index
                if cond is not None:
                    return (elem, cond)
                else:
                    return (elem, _condition.NoneCondition())
            else:  # ElementType
                return (index, _condition.NoneCondition())

        ForallType = List[Tuple[_variable.Element, _condition.Condition]]
        self._forall: ForallType = [convert_to_element(elem) for elem in forall_list]

        # type validation
        check_type(self.label, str)
        check_type(self._penalty_term, _expression.Expression)
        check_type(self._with_multiplier, bool)

    @property
    def label(self) -> str:
        return self._label

    @property
    def penalty_term(self) -> _expression.Expression:
        """Penalty term (without multiplier)."""
        return self._penalty_term

    @property
    def with_multiplier(self) -> bool:
        """Penalty term has lagrange muliplier or not."""
        return self._with_multiplier

    @property
    def forall(self):
        return self._forall

    def children(self):
        return [self.penalty_term]

    def __repr__(self) -> str:
        return f"Pena({self.label}: {self.penalty_term})"


ConstraintConditionType = Union[_condition.Equal, _condition.LessThanEqual]
ConstraintCondTypeValue = (_condition.Equal, _condition.LessThanEqual)


class Constraint(metaclass=_serializable.Serializable):
    """Constraint of optimization model."""

    def __init__(
        self,
        label: str,
        condition: Union[_expression.Expression, ConstraintConditionType],
        forall: Union[
            _variable.Element,
            Tuple[_variable.Element, Optional[_condition.Condition]],
            List[
                Union[
                    _variable.Element,
                    Tuple[_variable.Element, Optional[_condition.Condition]],
                ]
            ],
        ] = [],
        with_penalty: typ.Optional[bool] = None,
        with_multiplier: typ.Optional[bool] = None,
        left_lower: Union[
            _expression.NumericValue, _expression.Expression, None
        ] = None,
        auto_qubo: Optional[bool] = None,
    ):
        """
        Constraint of optimization model.

        Args:
            label (str): A unique identifier for the penalty term.
            condition (Union[CompareCondition, Expression]): constraint condition.
            forall (Element | Tuple[Element, Optional[Condition]] | List[Element | Tuple[Element, Optional[Condition]]], optional): A list of elements and optional conditions that the penalty term applies to. Default is an empty list.
            with_penalty (bool, optional): Add constraints as penalty. This argument is deprecated and will be removed in the next version. Defaults to True.
            with_multiplier (bool, optional): prod a multiplier on the penalty term. This argument is deprecated and will be removed in the next version. Defaults to True.
            left_lower: left hand side lower value. usually used for slack variables. This argument is deprecated and will be removed in the next version. Defaults to None.
            auto_qubo (bool, optional): auto qubo convert. This argument is deprecated and will be removed in the next version. Defaults to True.

        Examples:
            ```python
            import jijmodeling as jm
            n = jm.Placeholder("n")
            x = jm.Binary("x", shape=(n, ))
            term = jm.Constraint("const", x[:] == 1)
            ```

            constraint with forall

            ```python
            import jijmodeling as jm
            d = jm.Placeholder("d", dim=1)
            n = d.shape[0]
            x = jm.Binary("x", shape=(n, n))
            i = jm.Element("i", n)
            term = jm.Constraint("const2", x[i, :] == 1, forall=(i, d[i] > 0))
            ```

        Raises:
            TypeError: condition is not `CompareCondition` or `Experssion`.
            ExpressionValiddteError: right hand side has a desicision variable.
            TypeError: `left_lower` is not `numbers.Number` or `Expression`.
            TypeError: forall is not `Element`, `dict`, `tuple` or `list`.
            ExpressionIndexError: The indices have not been reduced and remains. Ex: `Sum(i, x[i,j,k]) == 1, forall=[j]`, In this case "k" is needed in forall.
            ExpressionIndexError: The conditions of indices have inconsistency.
        """

        self._label = label

        # deprecated
        warning_msg = "This optional argument will be removed in the next version."
        _deprecated.is_deprecated(
            "with_multiplier", with_multiplier, additional_msg=warning_msg
        )
        _deprecated.is_deprecated(
            "with_penalty", with_penalty, additional_msg=warning_msg
        )
        _deprecated.is_deprecated("left_lower", left_lower, additional_msg=warning_msg)
        _deprecated.is_deprecated("auto_qubo", auto_qubo, additional_msg=warning_msg)

        self._with_penalty = with_penalty if with_penalty is not None else True
        self._with_multiplier = with_multiplier if with_multiplier is not None else True

        # auto_qubo setting (automatically disabled if order >= 2 or term is
        # not a Condition)
        import jijmodeling.expression.utils as _utils

        if isinstance(condition, ConstraintCondTypeValue):
            order = max(
                _utils.get_order(condition.left), _utils.get_order(condition.right)
            )
            if order >= 2 and auto_qubo is None:
                auto_qubo = False
        elif isinstance(condition, _expression.Expression):
            if auto_qubo is None:
                auto_qubo = False
        else:
            raise TypeError(
                "condition of Constraint is <=, == or Expression, not {}.".format(
                    condition.__class__.__name__
                )
            )

        self._auto_qubo: bool = auto_qubo if auto_qubo is not None else True

        # convert Expression to Condition object
        self._condition: ConstraintConditionType = (
            condition
            if isinstance(condition, _condition.CompareCondition)
            else _condition.Equal(condition, _expression.Number(0))
        )

        # convert number object to Number object
        self._left_lower: Optional[_expression.Expression] = (
            _expression.Number(left_lower)
            if isinstance(left_lower, (int, float))
            else left_lower
        )

        # convert forall to list-type object
        forall_list = forall if isinstance(forall, list) else [forall]
        # element type from users
        IndexType = Union[
            _variable.Element, Tuple[_variable.Element, Optional[_condition.Condition]]
        ]

        @typechecked
        def convert_to_element(
            index: IndexType,
        ) -> Tuple[_variable.Element, _condition.Condition]:
            if isinstance(index, tuple):  # Tuple[ElementType, Condition]
                elem, cond = index
                if cond is not None:
                    return (elem, cond)
                else:
                    return (elem, _condition.NoneCondition())
            else:  # ElementType
                return (index, _condition.NoneCondition())

        ForallType = List[Tuple[_variable.Element, _condition.Condition]]
        self._forall: ForallType = [convert_to_element(elem) for elem in forall_list]

        # type validation
        LeftLowerType = Optional[_expression.Expression]
        check_type(self.label, str)
        check_type(self._condition, _condition.CompareCondition)
        check_type(self._forall, ForallType)
        check_type(self._with_penalty, bool)
        check_type(self._with_multiplier, bool)
        check_type(self._left_lower, LeftLowerType)
        check_type(self._auto_qubo, bool)

        import jijmodeling.expression.extract as _extract

        if isinstance(self._left_lower, _expression.Expression):
            if _extract.has_decivar(self._left_lower):
                raise _exceptions.CannotContainDecisionVarError(
                    "You cannot include decision variables in left_lower."
                )

        # check forall index reduction
        indices = _utils.condition_indices(self._condition)
        forall_labels = [index[0].label for index in self._forall]
        for index in indices:
            if index.label not in forall_labels:
                raise _exceptions.ExpressionIndexError(
                    "Constraint cannot have unreducted subscripts."
                    + " Please check your formulation or"
                    + f" use forall to reduct index '{index.label}'."
                )
        # condition index check
        # Ensure there are no contradictions in the dependency between indices entering the condition
        # For example, [(i, i < j), j] is fine because j is processed in the outer loop,
        # but [j, (i, i < j)] is not good because j is processed in the inner loop.
        for i, (_, cond) in enumerate(self._forall):
            if isinstance(cond, _condition.NoneCondition):
                continue
            cond_indices = _utils.condition_indices(cond)
            for ind in cond_indices:
                # but [j, (i, i < j)] is not good because j is processed in the inner loop.
                if not (ind.label in forall_labels[: i + 1]):
                    raise _exceptions.ExpressionIndexError(
                        "Check the conditions you are including in forall. There is a discrepancy in the subscript dependency."
                    )

    @property
    def label(self) -> str:
        return self._label

    @property
    def condition(self) -> ConstraintConditionType:
        return self._condition

    @property
    def term(
        self,
    ) -> Union[_condition.Equal, _condition.LessThanEqual, _condition.LessThan]:
        return self.condition

    @property
    def with_penalty(self) -> bool:
        return self._with_penalty

    @property
    def with_multiplier(self) -> bool:
        return self._with_multiplier

    @property
    def forall(self) -> List[Tuple[_variable.Element, _condition.Condition]]:
        return self._forall

    @property
    def left_lower(self) -> Optional[_expression.Expression]:
        return self._left_lower

    @property
    def auto_qubo(self):
        return self._auto_qubo

    def _forall_to_sum(self, expression):
        indices = self.forall[::-1]
        if indices is None:
            return expression
        term = expression
        for i, index in enumerate(indices):
            if index is None:
                return expression
            cond = indices[i][1]
            term = _sum.Sum((index[0], cond), term)
        return term

    def __repr__(self):
        return "Cons(" + self.label + ")[" + str(self.condition) + "]"
