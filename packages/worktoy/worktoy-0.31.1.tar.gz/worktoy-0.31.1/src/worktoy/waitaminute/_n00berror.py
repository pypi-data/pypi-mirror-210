"""n00bError should be raised when n00b developers are doing n00b things
that does not directly cause immediate pain. For example, if a n00b
developer does not use typehints:
  typeGuardFunction(n00bFunction, return_=str)


"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.waitaminute import ExceptionCore


class n00bError(ExceptionCore):
  """n00bError should be raised when n00b developers are doing n00b things
  that does not directly cause immediate pain. For example, if a n00b
  developer does not use typehints
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def __init__(self, *args, **kwargs) -> None:
    ExceptionCore.__init__(self, *args, **kwargs)

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    args = [*args, None]
    self._msg = args[0]
    return self._msg
