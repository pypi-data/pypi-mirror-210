"""The plenty function takes an arbitrary number of positional arguments
and checks if they are all different from None and returns True if so."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations


def plenty(*args) -> bool:
  """The plenty function takes an arbitrary number of positional arguments
  and checks if they are all different from None and returns True if so.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  for arg in args:
    if arg is None:
      return False
  return True
