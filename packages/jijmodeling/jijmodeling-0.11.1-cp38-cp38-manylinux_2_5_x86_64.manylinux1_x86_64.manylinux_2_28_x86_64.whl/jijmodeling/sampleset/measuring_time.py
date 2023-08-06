from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from jijmodeling.exceptions import SerializeSampleSetError
from jijmodeling.sampleset.solving_time import SolvingTime
from jijmodeling.sampleset.system_time import SystemTime


@dataclass
class MeasuringTime:
    """Schema for measuring time.

    Attributes:
        solve (Optional[SolvingTime], optional): Instance of SolvingTime. This means solver running time. Defaults to None.
        system (Optional[SystemTime], optional): Instance of SystemTime. This means time about jijzept system. Defaults to None.
        total (Optional[float], optional): Total time from submitting problem to obtaining solution. Defaults to None.
    """

    solve: Optional[SolvingTime] = None
    system: Optional[SystemTime] = None
    total: Optional[float] = None

    def __post_init__(self):
        if self.solve is None:
            self.solve = SolvingTime()
        if self.system is None:
            self.system = SystemTime()

    @classmethod
    def from_serializable(cls, obj: Dict):
        """To MeasuringTime object from Dict of SampleSet.

        Args:
            obj (Dict): Dict of MeasuringTime.

        Returns:
            MeasuringTime: MeasuringTime obj.
        """

        for key in ["solve", "system", "total"]:
            if key not in obj.keys():
                raise SerializeSampleSetError(f'"obj" does not contain "{key}" key')

        if obj["solve"] is None:
            solving_time = None
        else:
            solving_time = SolvingTime.from_serializable(obj["solve"])

        if obj["system"] is None:
            system_time = None
        else:
            system_time = SystemTime.from_serializable(obj["system"])
        return cls(
            solve=solving_time,
            system=system_time,
            total=obj["total"],
        )
