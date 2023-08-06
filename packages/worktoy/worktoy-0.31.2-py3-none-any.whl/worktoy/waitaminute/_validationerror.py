"""ValidationError is raised by the Marker system when a decorated class
fails a validation check."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from typing import NoReturn

from worktoy.waitaminute import ExceptionCore


class ValidationError(ExceptionCore):
  """ValidationError is raised by the Marker system when a decorated class
  fails a validation check.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    self._msg = args[0]
    return self._msg
