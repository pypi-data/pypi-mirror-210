from __future__ import annotations

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

import jijmodeling.protobuf.from_protobuf.from_protobuf as from_protobuf

__all__ = ["from_protobuf"]
