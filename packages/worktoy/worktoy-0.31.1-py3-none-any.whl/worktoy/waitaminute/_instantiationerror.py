"""InstantiationError should be raised by classes that do not allow
instantiation. """
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.stringtools import justify
from worktoy.waitaminute import ExceptionCore


class InstantiationError(ExceptionCore):
  """InstantiationError should be raised by classes that do not allow
  instantiation.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def _createMsg(self, cls: type = None, *args, **kwargs) -> str:
    """Reimplementation"""
    if type is None:
      self._msg = justify("""Attempted to instantiate unknown class which 
      does not permit instantiation!""")
      return self._msg
    self._msg = justify("""Attempted to instantiate unknown class which 
    does not permit instantiation!""")
    return self._msg
