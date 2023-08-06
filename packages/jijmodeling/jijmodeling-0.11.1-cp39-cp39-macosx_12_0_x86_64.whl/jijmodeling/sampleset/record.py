from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd

from jijmodeling.exceptions import SerializeSampleSetError
from jijmodeling.type_annotations import DenseSolution, SparseSolution


@dataclass
class Record:
    """Represents the Schema for solutions obtained by a solver.

    Attributes:
        solution (Dict[str, Union[List[SparseSolution], List[DenseSolution]]]): Solution. A key is the label of a decision variable. There are two type in value:
            - SparseSolution is tuple of length 3, where each element means (nonzero index, nonzero value, shape) for solution.
            - DenseSolution is numpy.ndarray which dimension is shape of decision variable.
        num_occurrences (List[int]): Number of occurrences for each sample.
    """

    solution: Dict[str, Union[List[SparseSolution], List[DenseSolution]]]
    num_occurrences: List[int]

    def __post_init__(self):
        self._is_dense = False
        self._current_index = 0

    def __len__(self) -> int:
        """
        Perform the operation __len__.
        """
        return len(self.num_occurrences)

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index == len(self):
            self._current_index = 0
            raise StopIteration()
        ret = self[self._current_index]
        self._current_index += 1
        return ret

    def __getitem__(
        self, item: Union[int, slice, List[int], Tuple[int], np.ndarray]
    ) -> Record:
        """Perform the operation __getitem__.

        Args:
            item (Union[int, slice, List[int], Tuple[int], np.ndarray]): Index of solution and num_occurrences.

        Returns:
            Record: Record object.
        """

        if isinstance(item, int):
            start, stop, step = item, item + 1, None
            solution = {
                label: solution[start:stop:step]
                for label, solution in self.solution.items()
            }
            return Record(
                solution=solution,
                num_occurrences=self.num_occurrences[start:stop:step],
            )
        elif isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step
            solution = {
                label: solution[start:stop:step]
                for label, solution in self.solution.items()
            }
            return Record(
                solution=solution,
                num_occurrences=self.num_occurrences[start:stop:step],
            )
        elif isinstance(item, (list, tuple, np.ndarray)):
            item = np.array(item) if len(item) else np.array([], dtype=int)
            if item.dtype == int or item.dtype == bool:
                index = np.arange(len(item))[item] if item.dtype == bool else item
                solution = {
                    label: [solution[i] for i in index]
                    for label, solution in self.solution.items()
                }
                num_occurrences = np.array(self.num_occurrences)[item].tolist()
                return Record(solution=solution, num_occurrences=num_occurrences)
            else:
                raise IndexError(f'Element of "{item}" must be int or bool.')
        else:
            raise IndexError(
                f'Type of index "{item}" must be one of int or slice or List[int] or Tuple[int] or 1d numpy.ndarray.'
            )

    @property
    def is_dense(self) -> bool:
        """SparseSolution or DenseSolution:
            - If True, DenseSolution,
            - Else, SparseSolution.

        Returns:
            bool: True or False.
        """
        return self._is_dense

    @is_dense.setter
    def is_dense(self, b: bool):
        self._is_dense = b

    @classmethod
    def from_serializable(cls, obj: Dict):
        """To Record object from Dict of SampleSet.

        Args:
            obj (Dict): Dict of Record.

        Returns:
            Record: Record obj.
        """

        for key in ["solution", "num_occurrences"]:
            if key not in obj.keys():
                raise SerializeSampleSetError(f'"obj" does not contain "{key}" key')
        return cls(**obj)

    def to_pandas_dataframe(self) -> pd.DataFrame:
        """Convert Record object to pandas.DataFrame object.

        Returns:
            pandas.DataFrame: pandas.DataFrame object.
        """
        solution = pd.DataFrame({f"solution[{k}]": v for k, v in self.solution.items()})
        num_occurrences = pd.DataFrame({"num_occurrences": self.num_occurrences})
        return pd.concat([solution, num_occurrences], axis=1)

    def to_dense(self, inplace: bool = False):
        solution = {}
        for label, si in self.solution.items():
            array_list = []
            for nonzero_index, values, shape in si:
                array = np.zeros(shape)
                if array.ndim:
                    array[nonzero_index] = values
                else:
                    array = np.array(values or 0)
                array_list.append(array)
            solution[label] = array_list
        if inplace:
            self.solution = solution
            self._solution_type = DenseSolution
        return Record(solution=solution, num_occurrences=self.num_occurrences)

    def _extend(self, other):
        for var_label, solution in other.solution.items():
            self.solution[var_label].extend(solution)
        self.num_occurrences.extend(other.num_occurrences)
