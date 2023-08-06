from __future__ import annotations

import copy as _copy
import enum as _enum
import typing as tp

import typeguard as _typeguard

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.constraint as _constraint
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.serializable as _serializable
import jijmodeling.expression.utils as _utils


class ProblemSense(_enum.Enum):
    """Problem sense.

    Attributes:
        MINIMUM (str): minimize problem.
        MAXIMUM (str): maximize problem.
    """

    MINIMUM = "MINIMUM"
    MAXIMUM = "MAXIMUM"


class Problem(metaclass=_serializable.Serializable):
    """
    Optimization problem.

    Attributes:
        name (str): name of problem.
        model (Optional[Expression]): total optimization model.
        constraints (Dict[str, Constraint]): constraint objects of problem.
        penalties (Dict[str, Constraint]): penalty objects of problem.
        cost (Expression): cost term of problem. Defaults zero.
    """

    def __init__(
        self,
        name: str,
        sense: tp.Union[ProblemSense, str] = ProblemSense.MINIMUM,
        objective: _expression.Expression = _expression.Number(0),
        constraints: tp.Dict[str, _constraint.Constraint] = {},
        penalties: tp.Dict[str, _constraint.Penalty] = {},
    ) -> None:
        """
        Initialize

        Args:
            problem_name (str): problem name
            kind (ProblemKind): problem kind Minimum or Maximum
            objective (Expression): objective
            constraints (Dict[str, Constraint]): dict of constraints
            penalties (Dict[str, Penalty]): dict of penalties
        """
        self._name = name
        self._sense = ProblemSense(sense)
        # deepcopy to avoid having the same reference
        self._objective = _copy.deepcopy(objective)
        self._constraints: tp.Dict[str, _constraint.Constraint] = _copy.deepcopy(
            constraints
        )
        self._penalties: tp.Dict[str, _constraint.Penalty] = _copy.deepcopy(penalties)

        _typeguard.check_type(self._name, str)
        _typeguard.check_type(self._sense, ProblemSense)
        _typeguard.check_type(self._constraints, tp.Dict[str, _constraint.Constraint])
        _typeguard.check_type(self._penalties, tp.Dict[str, _constraint.Penalty])

    @property
    def name(self) -> str:
        return self._name

    @property
    def sense(self) -> ProblemSense:
        return self._sense

    @property
    def objective(self) -> _expression.Expression:
        return self._objective

    @property
    def constraints(self) -> tp.Dict[str, _constraint.Constraint]:
        return self._constraints

    @property
    def penalties(self) -> tp.Dict[str, _constraint.Penalty]:
        return self._penalties

    def add(
        self,
        other: tp.Union[
            _expression.Expression, _constraint.Constraint, _constraint.Penalty
        ],
    ):
        """
        Add expression, constraint or penalty to problem.

        Args:
            other (Expression): expression

        Examples:
            ```python
            import jijmodeling as jm
            d = jm.Placeholder("d", dim=1)
            n = d.shape[0]
            i = jm.Element("i", n)
            x = jm.Binary("x", shape=(n,))
            problem = jm.Problem("sample")
            problem.add(x[:])  # add cost
            problem.add(jm.Constraint("onehot", x[:] == 1)) # add constraint
            problem.add(jm.Penalty("penalty", x[0] + x[2])) # add penalty
            problem += x[:] # syntax sugar `+=`
            problem += jm.Constraint("onehot", jm.Sum(i, d[i]*x[i]) <= 3)
            ```
        """
        if not isinstance(
            other,
            (
                int,
                float,
                _expression.Expression,
                _constraint.Constraint,
                _constraint.Penalty,
            ),
        ):
            raise TypeError(f"could not add {type(other)} to Problem.")
        # extract constraints
        if isinstance(other, _expression.Expression):
            # check index dependencies
            indices = _utils.expression_indices(other)
            if len(indices) > 0:
                raise _exceptions.ModelingError(
                    "{} depends on {}. The dependence on subscripts needs to be eliminated.".format(
                        other, indices
                    )
                )
            self._objective += other
        elif isinstance(other, _constraint.Constraint):
            # TODO CHECK CONSTRAINT SUBSCRIPTION DEPENDENCES
            self._constraints[other.label] = other
        elif isinstance(other, _constraint.Penalty):
            # check index dependencies
            term = other.penalty_term
            indices = _utils.expression_indices(term)
            if len(indices) > len(other.forall):
                raise _exceptions.ModelingError(
                    "{} depends on {}. The dependence on subscripts needs to be eliminated.".format(
                        term, indices
                    )
                )
            self._penalties[other.label] = other

    def __add__(
        self,
        other: tp.Union[
            _expression.Expression, _constraint.Constraint, _constraint.Penalty
        ],
    ) -> Problem:
        self.add(other)
        return self

    def _repr_latex_(self) -> str:
        from jijmodeling.latex_repr.problem_latex_repr import problem_latex_repr

        latex_repr = problem_latex_repr(self)
        return r"$$\begin{alignat*}{4}" + latex_repr + r"\end{alignat*}$$"
