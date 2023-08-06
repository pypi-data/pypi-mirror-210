from __future__ import annotations

import datetime as dt

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import orjson
import pandas as pd

from jijmodeling.exceptions import SampleSetNotEvaluatedError, SerializeSampleSetError
from jijmodeling.sampleset.evaluation import Evaluation
from jijmodeling.sampleset.measuring_time import MeasuringTime
from jijmodeling.sampleset.record import Record


@dataclass
class SampleSet:
    """Schema for sampleset.

    Attributes:
        record (Record): Record object. This means basic infomation of solutions.
        evaluation (Evaluation): Evaluation object. This means evaluation results of solutions.
        measuring_time (MeasuringTime): MeasuringTime object. This means measuring time of various processing until solutions is obtained.
    """

    record: Record
    evaluation: Evaluation
    measuring_time: MeasuringTime

    def __post_init__(self):
        self._is_dense = False
        self._current_index = 0
        self._metadata = {}

    def __len__(self) -> int:
        """
        Perform the operation __len__.
        """
        return self.record.__len__()

    def __iter__(self):
        """
        Perform the operation __iter__.
        """
        return self

    def __next__(self):
        """
        Perform the operation __next__.
        """
        if self._current_index == len(self):
            self._current_index = 0
            raise StopIteration()
        ret = self[self._current_index]
        self._current_index += 1
        return ret

    def __getitem__(
        self, item: Union[int, slice, List[int], Tuple[int], np.ndarray]
    ) -> SampleSet:
        """Perform the operation __getitem__.

        Args:
            item (Union[int, slice, List[int], Tuple[int], np.ndarray]): Index of sampleset.

        Returns:
            Record: SampleSet object.
        """
        record = self.record[item]
        evaluation = self.evaluation[item]
        return SampleSet(
            record=record, evaluation=evaluation, measuring_time=self.measuring_time
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

    @property
    def metadata(self) -> Dict:
        """Store information which is not in SampleSet schema.

        Returns:
            dict: Metadata.
        """
        return self._metadata

    @is_dense.setter
    def is_dense(self, b: bool):
        self._is_dense = b

    def to_pandas_dataframe(self) -> pd.DataFrame:
        """Convert SampleSet object to pandas.DataFrame object.

        Returns:
            pandas.DataFrame: pandas.DataFrame object.
        """
        record = self.record.to_pandas_dataframe()
        evaluation = self.evaluation.to_pandas_dataframe()

        return pd.concat([record, evaluation], axis=1)

    def to_dense(self, inplace: bool = False) -> SampleSet | None:
        """Convert SparseSolution to DenseSolution.

        Args:
            inplace (bool, optional): Modify the SampleSet object in place (do not create a new object). Defaults to False.

        Returns:
            SampleSet or None: SampleSet with dense solution or None if inplace=True.
        """
        if self.is_dense:
            if inplace:
                return None
            else:
                return self
        elif inplace:
            self.record.to_dense(inplace=inplace)
            self._is_dense = True
            return None
        else:
            record = self.record.to_dense(inplace=inplace)
            sampleset = SampleSet(
                record=record,
                evaluation=self.evaluation,
                measuring_time=self.measuring_time,
            )
            sampleset.is_dense = True
            return sampleset

    @classmethod
    def from_serializable(cls, obj: Dict):
        """To SampleSet object from Dict of SampleSet.

        Args:
            obj (Dict): Dict of SampleSet.

        Returns:
            SampleSet: SampleSet obj.
        """
        for key in ["record", "evaluation", "measuring_time"]:
            if key not in obj.keys():
                raise SerializeSampleSetError(f'"obj" does not contain "{key}" key')

        if "metadata" in obj:
            if isinstance(obj["metadata"], dict):
                metadata = obj["metadata"]
            else:
                raise TypeError('Type of "metadata" must be dict')
        else:
            metadata = {}

        solution = {}
        for k, v in obj["record"]["solution"].items():
            solution[k] = [(tuple(vi[0]), vi[1], tuple(vi[2])) for vi in v]
        obj["record"]["solution"] = solution

        record = Record.from_serializable(obj["record"])
        evaluation = Evaluation.from_serializable(obj["evaluation"])
        measuring_time = MeasuringTime.from_serializable(obj["measuring_time"])

        sampleset = cls(
            record=record,
            evaluation=evaluation,
            measuring_time=measuring_time,
        )
        sampleset.metadata.update(metadata)

        return sampleset

    def to_serializable(self) -> Dict:
        """To Dict of SampleSet from SampleSet object.

        Returns:
            SampleSet: Dict of SampleSet.
        """

        def default(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj

        evaluation_to_serializable_obj = self.evaluation.to_serializable()
        to_serializable_obj = asdict(self)
        to_serializable_obj["evaluation"] = evaluation_to_serializable_obj
        json_metadata = orjson.dumps(
            self.metadata,
            default=default,
            option=orjson.OPT_SERIALIZE_NUMPY,
        )
        to_serializable_obj["metadata"] = orjson.loads(json_metadata)
        return to_serializable_obj

    def feasible(self, rtol: float = 1e-05, atol: float = 1e-08):
        """Return feasible solutions.
        This function uses `np.isclose` to check feasibility.

        Args:
            rel_tol (float, optional): Relative tolerance. Defaults to 1e-05.
            abs_tol (float, optional): Absolute tolerance. Defaults to 1e-08.

        Returns:
            SampleSet: Output only feasible solutions from self.record.solution.
        """

        if self.evaluation.constraint_violations is None:
            raise SampleSetNotEvaluatedError("Your SampleSet object is not evaluated.")
        else:
            constraint_violations = np.array(
                list(self.evaluation.constraint_violations.values())
            )
            if len(constraint_violations):
                is_feas = np.isclose(
                    constraint_violations.sum(axis=0),
                    0,
                    rtol=rtol,
                    atol=atol,
                )
                return SampleSet(
                    record=self.record[is_feas],
                    evaluation=self.evaluation[is_feas],
                    measuring_time=self.measuring_time,
                )
            else:
                return self

    def infeasible(self):
        """Return infeasible solutions.

        Returns:
            SampleSet: Output only feasible solutions from self.record.solution.
        """
        if self.evaluation.constraint_violations is None:
            raise SampleSetNotEvaluatedError("Your SampleSet object is not evaluated.")
        else:
            constraint_violations = np.array(
                list(self.evaluation.constraint_violations.values())
            )
            if len(constraint_violations):
                is_infeas = constraint_violations.sum(axis=0) != 0
                return SampleSet(
                    record=self.record[is_infeas],
                    evaluation=self.evaluation[is_infeas],
                    measuring_time=self.measuring_time,
                )
            else:
                return self[[]]

    def lowest(self):
        """Return solutions with lowest objective in feasible solutions.

        Returns:
            SampleSet: Output only lowest objecive solutions in feasibles from self.record.solution.
        """

        if self.evaluation.objective is None:
            raise SampleSetNotEvaluatedError("Your SampleSet object is not evaluated.")
        else:
            feas = self.feasible()
            objective = np.array(feas.evaluation.objective)
            is_lowest = objective == objective.min() if len(objective) else []
            return SampleSet(
                record=feas.record[is_lowest],
                evaluation=feas.evaluation[is_lowest],
                measuring_time=feas.measuring_time,
            )

    def get_backend_calculation_time(self):
        """You can check calculation time for each process in detail.

        Returns:
            Dict: Processed metadata for describing JijZept backends.
        """

        def _get_root_keys(obj: Dict):
            if not isinstance(obj, dict):
                raise TypeError(f"Type of 'obj' must be Dict, not {obj.__class__}.")

            root_keys = []
            for k, v in obj.items():
                if isinstance(v, dict):
                    parent_id = v.get("parent_id", "")
                    if parent_id is None:
                        root_keys.append(k)
            return root_keys

        def _timedelta(start: str, end: str):
            s = dt.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
            e = dt.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")
            return (e - s).total_seconds()

        def _get_timedelata_by_span(obj: Dict, res: Optional[Dict] = None):
            if res is None:
                res = {}

            for k, v in obj.items():
                if isinstance(v, dict):
                    if "start_time" in v:
                        res[k] = {
                            "time": _timedelta(v["start_time"], v["end_time"]),
                            "span_id": v["context"]["span_id"],
                            "parent_id": v["parent_id"],
                        }
                    else:
                        res[k] = _get_timedelata_by_span(v, {})
            return res

        def _aggregate(obj: Dict, root_key: str, res: Optional[Dict] = None):
            if res is None:
                v = obj.pop(root_key, None)
                if v is None:
                    return {}
                else:
                    res = {
                        root_key: {
                            "id": v["span_id"],
                            "time": v["time"],
                        }
                    }
            for v_res in res.values():
                time_map = {
                    k: {"id": v["span_id"], "time": v["time"]}
                    for k, v in obj.items()
                    if v.get("parent_id", "") == v_res["id"]
                }

                if time_map:
                    del v_res["id"], v_res["time"]
                    v_res.update(_aggregate(obj, root_key, time_map))
                else:
                    del v_res["id"]
            return res

        def _reformat(obj: Dict):
            for k, v in obj.items():
                if isinstance(v, dict):
                    if "time" in v:
                        obj[k] = v["time"]
                    else:
                        obj[k] = _reformat(v)
            return obj

        root_keys = _get_root_keys(self.metadata)
        time = {}
        for root_key in root_keys:
            metadata = _get_timedelata_by_span(self.metadata)
            metadata = _aggregate(metadata, root_key)
            metadata = _reformat(metadata)
            time.update(metadata)
        return time

    def _extend(self, other):
        self.record._extend(other.record)
        self.evaluation._extend(other.evaluation)
        # TODO: concatenates MeasuringTime objects


def concatenate(
    jm_sampleset_list: List[SampleSet],
) -> SampleSet:
    """
    Concatenates SampleSet objects into a single SampleSet object.

    Args:
        jm_sampleset_list (List[SampleSet]): a list of SampleSet objects

    Returns:
        SampleSet: a SampleSet object that be concatenated
    """
    if len(jm_sampleset_list) == 0:
        raise ValueError("empty list is invalid")
    elif len(jm_sampleset_list) == 1:
        return jm_sampleset_list[0]
    else:
        concat_sampleset = deepcopy(jm_sampleset_list[0])
        for jm_sampleset in jm_sampleset_list[1:]:
            concat_sampleset._extend(jm_sampleset)
        return concat_sampleset
