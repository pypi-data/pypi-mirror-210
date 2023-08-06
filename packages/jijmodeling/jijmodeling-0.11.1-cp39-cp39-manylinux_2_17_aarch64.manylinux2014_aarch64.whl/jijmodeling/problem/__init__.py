from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

import jijmodeling.problem.problem as problem

from jijmodeling.problem.problem import Problem, ProblemSense

__all__ = ["problem", "ProblemSense", "Problem"]
