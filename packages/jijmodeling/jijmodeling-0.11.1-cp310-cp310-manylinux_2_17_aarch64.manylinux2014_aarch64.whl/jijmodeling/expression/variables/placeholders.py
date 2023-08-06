from __future__ import annotations

import typing as tp

from typeguard import check_type

import jijmodeling.expression.expression as _expression
import jijmodeling.expression.variables.variable as _variable


class Placeholder(_variable.Variable):
    """
    Placeholder variable.

    Variables for pouring in data when converting to QUBO or to MIP.
    When using the Placeholder class,
    you can specify the specific value to be placed in the Placeholder
    by using the `ph_value` argument of methods such as `.to_pyqubo` and `.to_lp` of the Problem class.
    If you want to handle array data that cannot be defined with shape (called jagged array), you can use the `JaggedArray` class.

    Example:
        ```python
        import jijmodeling as jm
        d = jm.Placeholder("d", dim=2)
        d.dim
        # 2
        k = jm.Placeholder("k", shape=(3, ))
        k.dim
        # 1
        ```
    """

    def __init__(
        self,
        label: str,
        dim: tp.Optional[int] = None,
        shape=None,
        uuid: tp.Optional[str] = None,
    ):
        if shape is not None:
            _shape = shape
        elif shape is None and dim is not None:
            _shape = tuple(None for _ in range(dim))
        else:
            _shape = []
        super().__init__(label, shape=_shape, uuid=uuid)


class ArrayShape(Placeholder):
    """
    Shape of variable.

    Example:
        ```python
        import jijmodeling as jm
        d = jm.Placeholder("d", dim=1)
        n = d.shape[0]
        print(type(n))
        # <class 'ArrayShape'>
        ```
    """

    def __init__(
        self,
        array: tp.Union[_variable.Variable, _variable.Subscripts],
        dimension: int,
        uuid: tp.Optional[str] = None,
    ):
        """
        Basically, a user does not call the constuctor directly; an object of.

        this class is created instead when shape value of a variable is None.

        Args:
            array (Variable): parent array
            dimension (int): dimension is corresponded this object.
        """
        self._array = array
        self._dimension = dimension

        # type and value validation
        ArrayType = tp.Union[_variable.Variable, _variable.Subscripts]
        check_type(self._array, ArrayType)
        check_type(self._dimension, int)

        super().__init__(str(self._array) + "_shape_%d" % dimension, uuid=uuid)

    @property
    def array(self):
        return self._array

    @property
    def array_dim(self):
        return self.array.dim

    @property
    def dimension(self):
        return self._dimension

    def is_operatable(self) -> bool:
        return True

    def children(self) -> tp.List[_expression.Expression]:
        return [self.array]

    def __hash__(self) -> int:
        return hash(self.label)
