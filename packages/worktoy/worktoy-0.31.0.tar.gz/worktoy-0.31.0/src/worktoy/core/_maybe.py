"""Documentation - maybe
The objective of the 'maybe' function is to implement the null-coalescence
behaviour in a None-aware way. It returns the first non-None argument
passed to it, or None if all arguments are None.

Inputs:
The function takes in any number of arguments of any type.

Flow:
The function iterates through all the arguments passed to it and checks if
each argument is not None. If it finds a non-None argument, it immediately
returns that argument. If it iterates through all the arguments and finds
that all of them are None, it returns None.

Outputs:
The function returns either the first non-None argument passed to it or
None if all arguments are None.

Additional aspects:
The function is None-aware, meaning it can handle None values as
arguments. The function is also licensed under the MIT License and was
created by Asger Jon Vistisen in 2023.
"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from typing import Any


def maybe(*args) -> Any:
  """The None-aware 'maybe' implements the null-coalescence behaviour.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  for arg in args:
    if arg is not None:
      return arg
  return None
