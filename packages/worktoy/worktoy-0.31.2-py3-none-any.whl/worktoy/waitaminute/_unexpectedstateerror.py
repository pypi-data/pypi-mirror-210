"""UnexpectedStateError should be raised when all alternate cases were
believed covered, but were not. For example,
  def apply(x: Any, f: CallMeMaybe) -> Any:
    if not isinstance(x, Numerical):
      return 0
    if isinstance(x, int):
      return x
    if isinstance(x, float):
      return int(round(x))
    raise UnexpectedStateError(x)
  apply(1j, lambda x: x)
"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.waitaminute import ExceptionCore


class UnexpectedStateError(ExceptionCore):
  """UnexpectedStateError should be raised when all alternate cases were
  believed covered, but were not. For example,
    def apply(x: Any, f: CallMeMaybe) -> Any:
      if not isinstance(x, Numerical):
        return 0
      if isinstance(x, int):
        return x
      if isinstance(x, float):
        return int(round(x))
      raise UnexpectedStateError
    apply(1j, lambda x: x)
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def __init__(self, *args, **kwargs) -> None:
    ExceptionCore.__init__(self, *args, **kwargs)

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    name = None
    if args:
      name = args[0]
    elif kwargs:
      name = [v for v in kwargs.values()][0]
    if name is None:
      self._msg = 'Reached unexpected state!'
      return self._msg
    self._msg = 'Variable %s was unexpectedly not recognized!' % name
    return self._msg
