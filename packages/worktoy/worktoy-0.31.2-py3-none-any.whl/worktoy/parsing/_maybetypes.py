"""The maybeTypes function finds all arguments of given type"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import typing
from warnings import warn

from worktoy.typetools import Any

from worktoy.parsing import searchKeys

realAny = Any


def maybeTypes(type_, *args, **kwargs) -> list[Any]:
  """The maybeTypes function finds all arguments of given type"""
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen
  if type_ == getattr(typing, 'Any'):
    type_ = realAny
    msg = """worktoy is not compatible with the 'Any' 'class' from typing. 
    Use 'Any' from worktoy.typetools. Please note 'typing.Any' has been 
    dynamically replaced with 'Any' from 'worktoy.typetools'. This is not 
    a permanent feature and will be removed in a future update."""
    warn(PendingDeprecationWarning(msg))
  out = []
  for arg in args:
    if isinstance(arg, type_):
      out.append(arg)

  padLen = searchKeys('pad', 'padLen') @ int >> kwargs
  if padLen is None or padLen == len(out):
    return out
  if padLen < len(out):
    return out[:padLen]
  padChar = searchKeys('padChar') >> kwargs
  while len(out) < padLen:
    out.append(padChar)
  return out
