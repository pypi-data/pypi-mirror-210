"""DIOError exceptions are raised by functions in the dio module."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.waitaminute import ExceptionCore


class DIOError(ExceptionCore):
  """DIOError exceptions are raised by functions in the dio module.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def __init__(self, *args, **kwargs) -> None:
    ExceptionCore.__init__(self, *args, **kwargs)
