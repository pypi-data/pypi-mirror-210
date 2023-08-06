"""The 'some' function takes an arbitrary number of positional arguments
and returns True if at least one such argument is different from None."""
#  MIT License
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from worktoy.core import maybe


def some(*args) -> bool:
  """The 'some' function takes an arbitrary number of positional arguments
  and returns True if at least one such argument is different from None.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  return True if maybe(*args, None) is not None else False
