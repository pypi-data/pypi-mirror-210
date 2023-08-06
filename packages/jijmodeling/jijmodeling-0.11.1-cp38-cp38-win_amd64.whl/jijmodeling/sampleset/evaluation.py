from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from jijmodeling.type_annotations import (
    ConstraintExpressionValuesType,
    ForallIndexType,
    ForallValuesType,
)


@dataclass
class Evaluation:
    """Schema for results of evaluating solutions.

    Attributes:
        energy (List[float]): a list of values of energy.
        objective (Optional[List[float]], optional): a list of values of objective function. Defaults to None.
        constraint_violations (Optional[Dict[str, List[float]]], optional): a list of constraint violations. A key is the name of a constraint. A value is cost of a constraint. Defaults to None.
        constraint_forall (Optional[ForallIndexType], optional): a list of indices of forall constraints. Defaults to None.
        constraint_values (Optional[List[ForallValuesType]], optional): a list of values of forall constraints. Defaults to None.
        penalty (Optional[Dict[str, List[float]]], optional): a list of costs of penalty terms. A key is the name of a penalty. A value is cost of a penalty term. Defaults to None.
    """

    energy: Optional[List[float]] = None
    objective: Optional[List[float]] = None
    constraint_violations: Optional[Dict[str, List[float]]] = None
    constraint_forall: Optional[ForallIndexType] = field(default=None, repr=False)
    constraint_values: Optional[List[ForallValuesType]] = field(
        default=None, repr=False
    )
    penalty: Optional[Dict[str, List[float]]] = None

    def __post_init__(self):
        self._current_index = 0

    def __len__(self) -> int:
        """
        Perform the operation __len__.
        """
        if self.energy is None:
            return 0
        else:
            return len(self.energy)

    def __iter__(self):
        return self

    def __next__(self):
        if self.energy is None:
            raise StopIteration()
        else:
            if self._current_index == len(self.energy):
                self._current_index = 0
                raise StopIteration()
            ret = self[self._current_index]
            self._current_index += 1
            return ret

    def __getitem__(
        self, item: Union[int, slice, List[int], Tuple[int], np.ndarray]
    ) -> Evaluation:
        """Perform the operation __getitem__.

        Args:
            item (Union[int, slice, List[int], Tuple[int], np.ndarray]): Index of evaluation metrics.

        Returns:
            Evaluation: Evaluation object.
        """

        def _slice(start: int, stop: int, step: Optional[int] = None) -> Evaluation:
            energy = None if self.energy is None else self.energy[start:stop:step]
            objective = (
                None if self.objective is None else self.objective[start:stop:step]
            )
            constraint_violations = (
                None
                if self.constraint_violations is None
                else {
                    label: constraint_violations[start:stop:step]
                    for label, constraint_violations in self.constraint_violations.items()
                }
            )
            constraint_values = (
                None
                if self.constraint_values is None
                else self.constraint_values[start:stop:step]
            )
            penalty = (
                None
                if self.penalty is None
                else {
                    label: penalty[start:stop:step]
                    for label, penalty in self.penalty.items()
                }
            )

            return Evaluation(
                energy=energy,
                objective=objective,
                constraint_violations=constraint_violations,
                constraint_forall=self.constraint_forall,
                constraint_values=constraint_values,
                penalty=penalty,
            )

        if isinstance(item, int):
            start, stop, step = item, item + 1, None
            return _slice(start, stop, step)
        elif isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step
            return _slice(start, stop, step)
        elif isinstance(item, (list, tuple, np.ndarray)):
            item = np.array(item) if len(item) else np.array([], dtype=int)
            if item.dtype == int or item.dtype == bool:
                energy = (
                    None
                    if self.energy is None
                    else np.array(self.energy)[item].tolist()
                )
                objective = (
                    None
                    if self.objective is None
                    else np.array(self.objective)[item].tolist()
                )
                constraint_violations = (
                    None
                    if self.constraint_violations is None
                    else {
                        label: np.array(constraint_violations)[item].tolist()
                        for label, constraint_violations in self.constraint_violations.items()
                    }
                )
                constraint_values = (
                    None
                    if self.constraint_values is None
                    else np.array(self.constraint_values)[item].tolist()
                )
                penalty = (
                    None
                    if self.penalty is None
                    else {
                        label: np.array(penalty)[item].tolist()
                        for label, penalty in self.penalty.items()
                    }
                )
                return Evaluation(
                    energy=energy,
                    objective=objective,
                    constraint_violations=constraint_violations,
                    constraint_forall=self.constraint_forall,
                    constraint_values=constraint_values,
                    penalty=penalty,
                )
            else:
                raise IndexError(f'Element of "{item}" must be int or bool.')
        else:
            raise IndexError(
                f'Type of index "{item}" must be int, slice, list[int], tuple[int, ...] or 1d numpy.ndarray.'
            )

    @property
    def constraint_expr_values(self) -> List[ConstraintExpressionValuesType] | None:
        """
        Values for each constraint. The values are stored in `Dict[Tuple[int, ...], float]` for each condition expanded by `forall`.
        """
        if self.constraint_forall is None:
            return None
        if self.constraint_values is None:
            return None

        expr_values = []
        for v in self.constraint_values:
            expr_values.append(
                {
                    const_name: {
                        tuple(i): vi
                        for i, vi in zip(
                            self.constraint_forall[const_name], v[const_name]
                        )
                    }
                    for const_name in self.constraint_forall
                }
            )
        return expr_values

    def to_pandas_dataframe(self) -> pd.DataFrame:
        """Convert Evaluation object to pandas.DataFrame object.

        Returns:
            pandas.DataFrame: pandas.DataFrame object.
        """

        evaluation = asdict(self)

        if evaluation["constraint_violations"]:
            constraint_violations = {
                f"constraint_violation[{k}]": v
                for k, v in evaluation.pop("constraint_violations").items()
            }
        else:
            constraint_violations = {}
            del evaluation["constraint_violations"]
        evaluation.update(constraint_violations)
        evaluation["constraint_forall"] = [self.constraint_forall] * len(self)

        if self.penalty:
            penalty = {f"penalty[{k}]": v for k, v in evaluation.pop("penalty").items()}
        else:
            penalty = {}
            del evaluation["penalty"]
        evaluation.update(penalty)

        return pd.DataFrame(evaluation)

    @classmethod
    def from_serializable(cls, obj: dict):
        """To Evaluation object from Dict of SampleSet.

        Args:
            obj (Dict): Dict of Evaluation.

        Returns:
            Evaluation: Evaluation obj.
        """

        return cls(
            energy=obj.get("energy"),
            objective=obj.get("objective"),
            constraint_violations=obj.get("constraint_violations"),
            constraint_forall=obj.get("constraint_forall"),
            constraint_values=obj.get("constraint_values"),
            penalty=obj.get("penalty"),
        )

    def to_serializable(self):
        return asdict(self)

    def _extend(self, other: Evaluation):
        if isinstance(other.energy, list):
            # Concatenate energy
            if self.energy is None:
                self.energy = other.energy
            else:
                self.energy.extend(other.energy)

        # Concatenate objective
        if isinstance(other.objective, list):
            if self.objective is None:
                self.objective = other.objective
            else:
                self.objective.extend(other.objective)

        # Concatenate constraint_violations
        if isinstance(other.constraint_violations, dict):
            if self.constraint_violations is None:
                self.constraint_violations = other.constraint_violations
            else:
                for (
                    con_label,
                    constraint_violation,
                ) in other.constraint_violations.items():
                    self.constraint_violations[con_label].extend(constraint_violation)

        # Overwrite constraint_forall
        # Since SampleSet assumes that it does not contain solutions for different problem or instance data,
        # the index of forall constraints (constraint_forall) are the same between the original SampleSet(self)
        # and combined SampleSet(other)."
        if isinstance(other.constraint_forall, dict):
            self.constraint_forall = other.constraint_forall

        if isinstance(other.constraint_values, list):
            if self.constraint_values is None:
                self.constraint_values = other.constraint_values
            else:
                self.constraint_values.extend(other.constraint_values)

        # Concatenate penalty
        if isinstance(other.penalty, dict):
            if self.penalty is None:
                self.penalty = other.penalty
            else:
                for pane_label, pena in other.penalty.items():
                    self.penalty[pane_label].extend(pena)
