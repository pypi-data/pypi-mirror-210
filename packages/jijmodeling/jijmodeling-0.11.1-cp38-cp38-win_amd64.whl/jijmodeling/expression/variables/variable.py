from __future__ import annotations

import typing as tp

from uuid import uuid4

from typeguard import check_type

import jijmodeling.exceptions.exceptions as _exceptions
import jijmodeling.expression.expression as _expression
import jijmodeling.expression.serializable as _serializable
import jijmodeling.expression.type_annotations as _type_annotations

if tp.TYPE_CHECKING:
    import jijmodeling.expression.sum as _sum


def type_check_bool(value, cls) -> bool:
    """
    Do a type_check_and returns whether the validation succeeds or not.

    Args:
        value: value to be validated
        cls: type

    Returns:
        bool: return if `value` matches the `cls` type.
    """
    try:
        check_type(value, cls)
    except TypeError:
        return False
    else:
        check_type(value, cls)

        return True


class Variable(_expression.Expression):
    """Abstract class for variables."""

    def __init__(
        self,
        label: str,
        shape: tp.Union[
            tp.Tuple[_type_annotations.ShapeElemInputType, ...],
            tp.List[_type_annotations.ShapeElemInputType],
            _type_annotations.ShapeElemInputType,
        ] = tuple([]),
        uuid: tp.Optional[str] = None,
    ):
        super().__init__(uuid=uuid)
        self._label = label

        # convert list to tuple
        _shape: tp.Tuple[tp.Optional[_type_annotations.ShapeElementType], ...]
        if isinstance(shape, (list, tuple)):
            _shape_list: tp.List[tp.Optional[_expression.Expression]] = []
            for s in shape:
                if s is None:
                    _shape_list.append(s)
                elif isinstance(s, _expression.Expression):
                    _shape_list.append(s)
                elif type_check_bool(s, _expression.NumericValue):
                    _shape_list.append(_expression.Number(int(s), dtype="int"))
                else:
                    raise TypeError("shape is Expression or int.")
            _shape = tuple(_shape_list)  # type: ignore
        elif shape is None:
            _shape = (None,)
        else:
            _shape = (_expression._numeric_to_expression(shape),)

        from jijmodeling.expression.variables.placeholders import ArrayShape

        _shape_value: tp.List[_type_annotations.ShapeElementType] = []
        for d, s in enumerate(_shape):
            if s is None:
                _shape_value.append(ArrayShape(self, d))
            else:
                _shape_value.append(s)

        self._shape_without_none = tuple(_shape_value)

        # The _shape should contain "None" to avoid circular references when serializing.
        # When serializing, "._shape" is referenced before "@property shape",
        # so this way we can avoid the problem of circular references.
        self._shape = _shape  # _shape attributes is for .children.

        import jijmodeling.expression.utils as _utils

        _utils.check_non_decision_variable(
            self._shape_without_none,
            "The shape cannot contain any decision variables. Check the shape of `{}`.".format(
                label
            ),
        )

        self._dummy_elements_id = [uuid4().hex for _ in range(self.dim)]

    @property
    def label(self) -> str:
        return self._label

    @property
    def shape(self) -> tp.Tuple[_type_annotations.ShapeElementType, ...]:
        return tuple(self._shape_without_none)

    @property
    def dim(self) -> int:
        return len(self.shape)

    def __repr__(self) -> str:
        return self.label

    def is_operatable(self) -> bool:
        return self.dim == 0

    def children(self) -> tp.List[_expression.Expression]:
        return [s for s in self._shape if s is not None]

    def __getitem__(
        self,
        key: tp.Union[
            _type_annotations.SubscriptElemInputType,
            tp.List[tp.Union[slice, _type_annotations.SubscriptElemInputType]],
            tp.Tuple[tp.Union[slice, _type_annotations.SubscriptElemInputType], ...],
        ],
    ) -> tp.Union[Subscripts, _sum.SumOperator]:
        """
        `[]` operator for adding subscripts if the user specifies str for the.

        argument which is available for previous versions of JijModeling
        (<=0.8.14), This function throws an error.

        Args:
            key : subscripts

        Raises:
            ModelingError: If there is a discrepancy between the dimension of the variable and the number of subscripts added.
            TypeError: key type check.

        Returns:
            Subscripted variable.
        """
        key_tuple: tp.Tuple[tp.Union[slice, _expression.Expression, int], ...]
        if isinstance(key, list):
            key_tuple = tuple(key)
        elif isinstance(key, (_expression.Expression, slice, int)):
            key_tuple = (key,)
        elif isinstance(key, tuple):
            key_tuple = key
        else:
            raise TypeError(
                "key is tp.List[Expression] or tp.Tuple[Expression] or Expression. not {}.".format(
                    key.__class__.__name__
                )
            )

        if self.dim < len(key_tuple):
            raise _exceptions.ModelingError(
                "{} is {}-dimentional array, not {}-dim.".format(
                    self, self.dim, len(key_tuple)
                )
            )

        subscripts: tp.List[_type_annotations.SubscriptElementType] = []
        summation_index: tp.List[Element] = []
        for i, k in enumerate(key_tuple):
            key_element: _expression.Expression
            if isinstance(k, slice):
                # syntax sugar
                # x[:] => Sum({':x_0': x.shape[0]}, x[':x_0'])

                subscripted_var = Subscripts(self, subscripts=subscripts[:i])
                element_set: _type_annotations.ShapeElementType = subscripted_var.shape[
                    0
                ]
                sum_element = Element(
                    f":{self.label}_{i}", element_set, uuid=self._dummy_elements_id[i]
                ).set_latex(rf"\bar{{i}}_{{{str(i)}}}")
                summation_index.append(sum_element)
                key_element = sum_element
            elif isinstance(k, _expression.Expression):
                key_element = k
            elif isinstance(k, int):
                key_element = _expression.Number(k, dtype="int")
            else:
                raise TypeError(
                    "subscripts of {} is ".format(k)
                    + "`int` or `Expression`, not {}.".format(type(k))
                )
            subscripts.append(key_element)

        variable: tp.Union[_sum.SumOperator, Subscripts] = Subscripts(
            self, subscripts=subscripts
        )
        import jijmodeling.expression.sum as _sum

        for index in summation_index:
            variable = _sum.Sum(index, variable)
        return variable

    def __hash__(self) -> int:
        return hash(self.label) + self.uuid.__hash__()


class Subscripts(_expression.Expression):
    def __init__(
        self,
        variable: Variable,
        subscripts: tp.List[_type_annotations.SubscriptElementType],
        uuid: tp.Optional[str] = None,
    ):
        super().__init__(uuid=uuid)

        self._variable = variable
        self._subscripts = subscripts

        from jijmodeling.expression.type_annotations import SubscriptElementType
        from jijmodeling.expression.utils import check_non_decision_variable

        check_type(subscripts, tp.List[SubscriptElementType])
        check_non_decision_variable(
            subscripts,
            "The subscripts cannot contain any decision variables. Check the shape of `{}`.".format(
                variable.label
            ),
        )
        for index in subscripts:
            if not index.is_operatable():
                raise _exceptions.ModelingError(
                    f"subscripts is operatable. `{index}` is not operatable (scalar) in which {self}. check the dimension of `{index}`."
                )

    @property
    def variable(self) -> Variable:
        return self._variable

    @property
    def subscripts(self) -> tp.List[_type_annotations.SubscriptElementType]:
        return self._subscripts

    @property
    def label(self):
        return self._variable.label

    def children(self) -> tp.List[_expression.Expression]:
        var_list: tp.List[_expression.Expression] = [self.variable]
        # type: ignore
        subscripts: tp.List[_expression.Expression] = self.subscripts
        return var_list + subscripts

    def is_operatable(self) -> bool:
        """
        Check scalar or not.

        If the subscripts are specified as many times as the dimension of the variable,
        the Subscripts object is 'operatable' because it is a scalar.

        Returns:
            bool: is operatable or not.
        """
        return self.variable.dim == len(self.subscripts)

    @property
    def shape(self):
        import jijmodeling.expression.variables.jagged_array as _jagged_array

        if isinstance(self.variable, _jagged_array.JaggedArray):
            import jijmodeling.expression.variables.placeholders as _placeholders

            return (_placeholders.ArrayShape(self, dimension=0),)
        else:
            return self.variable.shape[len(self.subscripts) :]

    @property
    def dim(self) -> int:
        return self.variable.dim - len(self.subscripts)

    def __repr__(self) -> str:
        subs = ",".join([str(s) for s in self.subscripts])
        repr_str: str = self.label + "[" + subs + "]"
        return repr_str

    def __getitem__(
        self,
        key: tp.Union[
            _type_annotations.SubscriptElemInputType,
            tp.List[tp.Union[slice, _type_annotations.SubscriptElemInputType]],
            tp.Tuple[tp.Union[slice, _type_annotations.SubscriptElemInputType], ...],
        ],
    ) -> tp.Union["Subscripts", _sum.SumOperator]:
        """
        Overload `[]` operator for adding subscripts if the user specifies str.

        for the argument which is available for previous versions of
        JijModeling (<=0.8.14), This function throws an error.

        Args:
            key : subscripts

        Raises:
            TypeError: key type check.

        Returns:
            Subscripted variable.
        """

        # convert to list
        key_list: tp.List[_type_annotations.SubscriptElemInputType]
        if isinstance(key, list):
            key_list = key
        elif isinstance(key, (_expression.Expression, slice)):
            key_list = [key]
        elif isinstance(key, int):
            key_list = [_expression.Number(key)]
        elif isinstance(key, tuple):
            key_list = list(key)
        else:
            raise TypeError(
                "key is tp.List[Expression] or tp.Tuple[Expression] or Expression. not {}.".format(
                    key.__class__.__name__
                )
            )

        # concat subscripts
        concat_subs: tp.List[tp.Union[slice, _expression.Expression, int]] = (
            self.subscripts + key_list
        )  # type: ignore
        return self.variable[concat_subs]


class Element(Variable):
    def __init__(self, label: str, parent, uuid: tp.Optional[str] = None):
        """
        Element object.

        Args:
            label (str): variable label
            parent (tp.Union[tp.Tuple[tp.Union[int, Expression], tp.Union[int, Expression]], Expression, int, Range]): parent of element

        Examples:
            ```python
            >>> import jijmodeling as jm
            >>> n = jm.Placeholder("n")
            >>> i = jm.Element("i", n)
            >>> i.parent
            (0, n)
            >>> jm.Element("i", (1, n)).parent
            (1, n)
            >>> V = jm.Placeholder("V")
            >>> i = jm.Element("i", V)  # represents i in V
            >>> i.parent
            V
            ````
        """
        if isinstance(parent, tuple):
            self._parent: tp.Union[Range, Variable] = Range(parent[0], parent[1])
        elif isinstance(parent, _expression.Expression):
            if parent.is_operatable():
                # operatable means parent is scalar.
                self._parent = Range(start=0, last=parent)
            else:
                # parent is not scalar. ex. i in V
                self._parent = parent  # type: ignore
        elif isinstance(parent, (int, float)):
            # parent is range. ex. i in V
            self._parent = Range(start=0, last=int(parent))
        elif isinstance(parent, Range):
            self._parent = parent
        else:
            raise TypeError(
                "'parent' is 'int', 'Expression' or 'tuple' not {}.".format(
                    type(parent)
                )
            )

        super().__init__(label=label, uuid=uuid)

    @property
    def parent(self) -> _type_annotations.ElementParentType:
        return self._parent

    def children(self) -> tp.List[_expression.Expression]:
        if isinstance(self.parent, Range):
            return [self.parent.start, self.parent.last]
        else:
            return [self.parent]

    @property
    def dim(self) -> int:
        if isinstance(self.parent, Range):
            return 0
        else:
            parant_dim = self.parent.dim
            return parant_dim - 1

    def is_operatable(self) -> bool:
        return self.dim == 0

    @property
    def shape(self) -> tp.Tuple[_type_annotations.ShapeElementType, ...]:
        from jijmodeling.expression.variables.placeholders import Placeholder

        if isinstance(self.parent, Range):
            return (self.parent.length(),)
        elif isinstance(self.parent, Placeholder):
            return self.parent.shape[1:]
        elif not self.is_operatable():
            from jijmodeling.expression.variables.placeholders import ArrayShape

            return (ArrayShape(self, dimension=0),)
        else:
            return ()


class Range(metaclass=_serializable.Serializable):
    def __init__(
        self,
        start: tp.Union[_expression.Expression, int],
        last: tp.Union[_expression.Expression, int],
        uuid: tp.Optional[str] = None,
    ) -> None:
        """
        Range object.

        Args:
            start (tp.Union[Expression, int]): range start
            last (tp.Union[Expression, int]): range last

        Examples:
            ```python
            >>> import jijmodeling as jm
            >>> n = jm.Placeholder('n')
            >>> r = jm.expression.variables.variable.Range(0,n)
            >>> r.start
            0
            >>> r.last
            n
            ```
        """
        if isinstance(start, _expression.Expression) and not start.is_operatable():
            raise _exceptions.ModelingError(
                "Range's start should be operatable. {} is not operatable.".format(
                    start
                )
            )
        if isinstance(last, _expression.Expression) and not last.is_operatable():
            raise _exceptions.ModelingError(
                "Range's last should be operatable. {} is not operatable.".format(last)
            )

        if not isinstance(start, _expression.Expression):
            self._start: _expression.Expression = _expression.Number(start, dtype="int")
        else:
            self._start = start

        if not isinstance(last, _expression.Expression):
            self._last: _expression.Expression = _expression.Number(last, dtype="int")
        else:
            self._last = last

        if uuid is None:
            self._uuid = uuid4().hex
        else:
            self._uuid = uuid

    @property
    def start(self) -> _expression.Expression:
        return self._start

    @property
    def last(self) -> _expression.Expression:
        return self._last

    @property
    def uuid(self) -> str:
        return self._uuid

    def length(self) -> _expression.Expression:
        length: _expression.Expression = self.last - self.start
        return length
