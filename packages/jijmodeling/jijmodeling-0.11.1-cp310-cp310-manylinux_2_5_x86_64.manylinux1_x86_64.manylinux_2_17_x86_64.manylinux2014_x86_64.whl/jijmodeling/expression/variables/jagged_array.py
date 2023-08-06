from __future__ import annotations

from typing import Optional, Tuple

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.type_annotations as _type_annotations
import jijmodeling.expression.variables.placeholders as _placeholders


class JaggedArray(_placeholders.Placeholder):
    """
    Jagged array: A data structure in which each element in a two-dimensional.

    array has a different length in a one-dimensional array. The internal
    length of the data is different, so `shape` is not defined. Only `shape[0]`
    can be accessed directly in `.shape`.

    A jagged array is an array with the following data structure, for example

    ```python
    [[1, 2, 3],
     [3, 2, 4, 5],
     [0, 1]]
    ```

    The Placeholder class can handle multi-dimensional arrays that can be defined with shape, but it cannot handle a jagged arrays.
    Therefore, we need to use this class instead.
    """

    def __init__(
        self,
        label: str,
        dim: int,
        uuid: Optional[str] = None,
    ):
        """
        Args:
            label (str): label of variable
            dim (int): dimension of jagged array. Because of the jagged array data structure, `shape` cannot be specified in the constructor.
            uuid (Optional[str], optional): uuid. Defaults to None.

        Raises:
            ModelingError: The jagged array can currently only handle up to two dimensions. This limitation will be resolved in an update.
        """

        if dim > 5:
            raise _exceptions.ModelingError(
                "JaggedArray must be set to 5-dim or less, not {}.".format(dim)
            )

        self._dim = dim
        super().__init__(label, dim, uuid=uuid)

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def shape(self) -> Tuple[_type_annotations.ShapeElementType]:
        """
        Shape cannot be defined in the jagged array.

        Only the length can be
        defined, so only the `.shape[0]` corresponding to the length is returned.

        Returns:
            Tuple[Expression]: (length, )
        """
        return (super().shape[0],)

    @property
    def length(self) -> _type_annotations.ShapeElementType:
        return self.shape[0]
