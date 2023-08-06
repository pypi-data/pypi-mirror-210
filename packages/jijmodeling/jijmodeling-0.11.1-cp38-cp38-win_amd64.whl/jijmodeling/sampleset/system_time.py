from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from jijmodeling.exceptions import SerializeSampleSetError


@dataclass
class SystemTime:
    """Schema for system of jijzept running time.

    Args:
        post_problem_and_instance_data (Optional[float], optional): Time to upload problem and instance_data to blob. Defaults to None.
        request_queue (Optional[float], optional): Time to send request to queue. Defaults to None.
        fetch_problem_and_instance_data (Optional[float], optional): Time to fetch problme and instance_data from blob. Defaults to None.
        fetch_result (Optional[float], optional): Time to fetch result. Defaults to None.
        deserialize_solution (Optional[float], optional): Time to deserialize json object. Defaults to None.
    """

    post_problem_and_instance_data: Optional[float] = None
    request_queue: Optional[float] = None
    fetch_problem_and_instance_data: Optional[float] = None
    fetch_result: Optional[float] = None
    deserialize_solution: Optional[float] = None

    @classmethod
    def from_serializable(cls, obj: Dict):
        """To SystemTime object from Dict of SampleSet.

        Args:
            obj (Dict): Dict of SystemTime.

        Returns:
            SystemTime: SystemTime obj.
        """

        for key in [
            "post_problem_and_instance_data",
            "request_queue",
            "fetch_problem_and_instance_data",
            "fetch_result",
            "deserialize_solution",
        ]:
            if key not in obj.keys():
                raise SerializeSampleSetError(f'"obj" does not contain "{key}" key')

        return cls(**obj)
