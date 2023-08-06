"""The maybeType function finds the first argument of a particular type"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import typing
from warnings import warn

from worktoy.typetools import Any

realAny = Any


def maybeType(type_: type, *args) -> Any:
  """The maybeType function finds the first argument of a particular type
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  if type_ == getattr(typing, 'Any'):
    type_ = realAny
    msg = """worktoy is not compatible with the 'Any' 'class' from typing. 
    Use 'Any' from worktoy.typetools. Please note 'typing.Any' has been 
    dynamically replaced with 'Any' from 'worktoy.typetools'. This is not 
    a permanent feature and will be removed in a future update."""
    warn(PendingDeprecationWarning(msg))
  for arg in args:
    if arg is not None:
      if isinstance(arg, type_):
        return arg
  return None
