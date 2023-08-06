import typing as typ
import warnings

ARG_VAL_TYPE = typ.TypeVar("ARG_VAL_TYPE")


def is_deprecated(
    arg_name,
    arg_value: typ.Optional[ARG_VAL_TYPE],
    default_value=None,
    additional_msg="",
) -> typ.Optional[ARG_VAL_TYPE]:
    if arg_value is not None:
        warnings.warn(f"{arg_name} is deprecated. " + additional_msg, FutureWarning)
        return arg_value
    else:
        return default_value
