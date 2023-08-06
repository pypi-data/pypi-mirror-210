from __future__ import annotations


class JijModelingError(Exception):
    """
    Exception for JijModeling Errors related to JijModeling inherit from this.

    Exception class.
    """


class ModelingError(JijModelingError):
    """
    Errors in constructing expressions.
    """


class CannotContainDecisionVarError(ModelingError):
    pass


class ExpressionIndexError(JijModelingError):
    pass


class DataError(JijModelingError):
    pass


class SerializeSampleSetError(JijModelingError):
    pass


class SampleSetNotEvaluatedError(JijModelingError):
    """
    Exception if sampleset is not evaluated.
    """
