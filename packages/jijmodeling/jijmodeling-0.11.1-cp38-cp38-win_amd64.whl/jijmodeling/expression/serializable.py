from __future__ import annotations

import abc as _abc
import enum as _enum
import inspect as _inspect
import typing as tp
import uuid as _uuid

from typeguard import typechecked

import jijmodeling


class Serializable(_abc.ABCMeta):
    """
    Meta class that can call `to_serializable()` and `from_serializable()`.
    """

    def __new__(cls, cls_name, cls_bases, cls_dict):
        if "__init__" in cls_dict:
            # serializeで用いるためExpressionクラスはコンストラクタの引数と対応する同じ名前の
            # @property を持つ必要があるので, それが実装されているかをチェックする
            init_func = _inspect.signature(cls_dict["__init__"])
            params = [param for param in init_func.parameters if param != "self"]
            for param in params:
                if param not in cls_dict:
                    bases_has_property = False
                    for bases in cls_bases:
                        if param in dir(bases):
                            bases_has_property = True
                    if not bases_has_property:
                        raise NotImplementedError(
                            f"propety '{param}' must be" + f" define in {cls_name}."
                        )
        return super().__new__(cls, cls_name, cls_bases, cls_dict)


def to_serializable(expression: Serializable) -> dict:
    """
    Serialize an serializable object.

    Args:
        expression (Serializable): e.g. mathematical expression, problem, ...

    Returns:
        dict: serialized object
    """
    seri = obj_to_seri(expression)
    return {"version": "0.10.0", "object": seri}


def obj_to_seri(obj):
    if isinstance(obj.__class__, Serializable):
        return expression_to_seri(obj)
    elif isinstance(obj, (list, tuple)):
        return {
            "iteratable": "list" if isinstance(obj, list) else "tuple",
            "value": [obj_to_seri(v) for v in obj],
        }
    elif isinstance(obj, dict):
        return {k: obj_to_seri(v) for k, v in obj.items()}
    elif isinstance(obj, _uuid.UUID):
        return obj.hex
    elif isinstance(obj, _enum.Enum):
        if isinstance(obj, jijmodeling.expression.expression.DataType):
            return obj.value.lower()
        else:
            return obj.value
    else:
        return obj


def expression_to_seri(expression: Serializable) -> dict:
    exp_module = expression.__class__.__module__
    exp_cls = expression.__class__.__name__
    serializable: tp.Dict[str, tp.Any] = {"class": exp_module + "." + exp_cls}

    init_args_keys = _inspect.getfullargspec(expression.__class__.__init__).args
    init_params = {}
    for key in init_args_keys:
        # Ignore `self` because it is not used as a key for a serialized object
        if key == "self":
            continue
        # Expression class の constructor の引数名と同じpropertyを必ず各クラスは持っているので
        # それを情報としてserializeする
        if f"_{key}" in dir(expression):
            value = eval(f"expression._{key}")
        else:
            value = eval(f"expression.{key}")
        init_params[key] = obj_to_seri(value)
    serializable["attributes"] = init_params
    return serializable


@typechecked
def from_serializable(serializable: tp.Union[dict, list]):
    """
    Convert to Expression from serializable object (dict).

    Args:
        serializable (dict): serialized object

    Returns:
        Expression|Problem: e.g. mathematical expression, problem, ...

    """
    if isinstance(serializable, dict) and "object" in serializable:
        obj = serializable["object"]
    else:
        raise ValueError("version mismatch")
    return obj_from_seri(obj)


def obj_from_seri(obj):
    if isinstance(obj, dict) and "class" in obj:
        modulePath = obj["class"].split(".")[1:]
        module = jijmodeling
        for m in modulePath:
            module = getattr(module, m)
        # get name of arguments of __init__ of Expression object
        init_args = _inspect.getfullargspec(module.__init__).args
        init_arg_values = {
            arg: obj_from_seri(obj["attributes"][arg])
            for arg in init_args
            if arg != "self"
        }
        return module(**init_arg_values)
    elif isinstance(obj, dict) and "iteratable" in obj:
        if obj["iteratable"] == "list":
            return [obj_from_seri(s) for s in obj["value"]]
        elif obj["iteratable"] == "tuple":
            return tuple(obj_from_seri(s) for s in obj["value"])
    elif isinstance(obj, list):
        return [obj_from_seri(s) for s in obj]
    elif isinstance(obj, dict):
        return {k: obj_from_seri(v) for k, v in obj.items()}

    return obj
