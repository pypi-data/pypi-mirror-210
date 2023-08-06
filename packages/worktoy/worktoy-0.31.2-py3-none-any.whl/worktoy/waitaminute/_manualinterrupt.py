"""ManualInterrupt should be raised when the program was stopped as a
result of developer action. Please note that this exception is unlikely to
find suitable use in production."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.waitaminute import ExceptionCore


class ManualInterrupt(ExceptionCore):
  """ManualInterrupt should be raised when the program was stopped as a
  result of developer action. Please note that this exception is unlikely to
  find suitable use in production.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    self._msg = 'Program aborted!'
    return self._msg
