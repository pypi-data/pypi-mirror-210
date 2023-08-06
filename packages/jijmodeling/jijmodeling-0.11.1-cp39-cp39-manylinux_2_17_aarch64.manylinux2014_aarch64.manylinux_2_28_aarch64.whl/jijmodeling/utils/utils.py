from __future__ import annotations

import functools
import inspect
import time
import typing as tp

from typing import Optional

import jijmodeling.exceptions.exceptions as _exceptions

from jijmodeling.type_annotations.type_annotations import FIXED_VARIABLES


def validate_value(
    condition_str: str, condition: bool, error_msg: Optional[str] = None
) -> None:
    if condition is False:
        raise _exceptions.ModelingError(
            f"The condition {condition_str} is not satisfied."
            if error_msg is None
            else error_msg
        )


FixedVariables = tp.Dict[str, tp.Dict[tp.Tuple[int, ...], tp.Union[int, float]]]
SerializedFixedVariables = tp.Dict[
    str, tp.List[tp.Union[tp.List[tp.List[int]], tp.List[tp.Union[int, float]]]]
]


T = tp.TypeVar("T")


def simple_list_validation(name: str, data: tp.List[T], inner: tp.Type[T]) -> bool:
    if not isinstance(data, list):
        raise TypeError(name + f" is list, not {data.__class__.__name__}.")

    if len(data) > 0:
        if not isinstance(data[0], inner):
            raise TypeError(name + f"[0] is {inner}, not {data[0].__class__.__name__}.")

    return True


K = tp.TypeVar("K")


def simple_dict_validation(
    name: str, data: tp.Dict[K, T], key_type: tp.Type[K], value_type: tp.Type[T]
) -> bool:
    if not isinstance(data, dict):
        raise TypeError(name + f" is dict, not {data.__class__.__name__}.")

    if len(data) > 0:
        keys = list(data.keys())
        values = list(data.values())
        if not isinstance(keys[0], key_type):
            raise TypeError(
                name
                + f"'s key `{keys[0]}` is {key_type}, not {keys[0].__class__.__name__}."
            )

        if not isinstance(values[0], key_type):
            raise TypeError(
                name
                + f"'s value `{values[0]}` is {value_type}, not {values[0].__class__.__name__}."
            )

    return True


def with_measuring_time(attr):
    def _with_measuring_time(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args = list(args)
            args += [
                v for k, v in kwargs.items() if k in inspect.signature(func).parameters
            ]
            if "system_time" in kwargs:
                s = time.time()
                ret = func(*args)
                if kwargs["system_time"] is not None:
                    setattr(kwargs["system_time"], attr, time.time() - s)
            elif "solving_time" in kwargs:
                s = time.time()
                ret = func(*args)
                if kwargs["solving_time"] is not None:
                    setattr(kwargs["solving_time"], attr, time.time() - s)
            else:
                ret = func(*args)
            return ret

        return wrapper

    return _with_measuring_time


def serialize_fixed_var(fixed_variables: FIXED_VARIABLES):
    """Serializes fixed variables.

    Args:
        fixed_variables (FixedVariables): obj to be serialized
    Returns:
        Dict[label, List[[index,...], [value,...]]]: serialized fixed variables
    """
    result = {}

    for deci_var, interaction_dict in fixed_variables.items():
        indices_list = []
        value_list = []
        for indices, value in interaction_dict.items():
            indices_list.append(list(indices))
            value_list.append(value)

        result[deci_var] = [indices_list, value_list]

    return result


def deserialize_fixed_var(obj):
    """Deserializes fixed variable.

    Args:
        obj (Dict[label, List[[index,...], [value,...]]]): serialized fixed variables
    Returns:
        FixedVariables:
    Raises:
        ValueError: If the lengh of list in fixed variables is not 2.
    """
    result = {}
    for var_label, index_value_list in obj.items():
        if len(index_value_list) != 2:
            raise ValueError(
                f"the length of list in fixed variables must be 2, but actually {len(index_value_list)}"
            )

        interaction_dict = {
            tuple(indices): val
            for indices, val in zip(index_value_list[0], index_value_list[1])
        }

        result[var_label] = interaction_dict

    return result
