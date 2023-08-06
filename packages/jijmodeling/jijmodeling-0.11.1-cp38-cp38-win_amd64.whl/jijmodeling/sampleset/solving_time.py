from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from jijmodeling.exceptions import SerializeSampleSetError


@dataclass
class SolvingTime:
    """Schema for solver running time.

    Attributes:
        preprocess (Optional[float], optional): Time to preprocess. Defaults to None.
        solve (Optional[float], optional): Time to solve. Defaults to None.
        postprocess (Optional[float], optional): Time to postprocess. Defaults to None.
    """

    preprocess: Optional[float] = None
    solve: Optional[float] = None
    postprocess: Optional[float] = None

    @classmethod
    def from_serializable(cls, obj: Dict):
        """To SolvingTime object from Dict of SampleSet.

        Args:
            obj (Dict): Dict of SolvingTime.

        Returns:
            SolvingTime: SolvingTime obj.
        """

        for key in ["preprocess", "solve", "postprocess"]:
            if key not in obj.keys():
                raise SerializeSampleSetError(f'"obj" does not contain "{key}" key')

        return cls(**obj)
