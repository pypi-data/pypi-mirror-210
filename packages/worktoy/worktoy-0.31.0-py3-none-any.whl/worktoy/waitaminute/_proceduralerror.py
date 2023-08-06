"""ProceduralError should be raised when a variable is defined in the
name space as expected, but is unexpectedly not ready. Typically, this
would be when a variable is added to the name space with a value of None
awaiting initialisation, but where another process requests it, whilst it
is still waiting."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from typing import Any

from worktoy.parsing import extractArg
from worktoy.stringtools import stringList
from worktoy.waitaminute import ExceptionCore


class ProceduralError(ExceptionCore):
  """ProceduralError requires the following arguments (name, type_, var,
  info):
  :param name: Name the variable
  :param type: Its expected type
  :param variable: The contents of the variable
  :param info: Optional explanatory note
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def __init__(self, *args, **kwargs) -> None:
    ExceptionCore.__init__(self, *args, **kwargs)

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    nameKeys = stringList('name, variable, id, varName')
    name, args, kwargs = extractArg(str, nameKeys, *args, **kwargs)
    typeKeys = stringList('type, type_, class, class_, expected')
    type_, args, kwargs = extractArg(type, typeKeys, *args, **kwargs)
    variableKeys = stringList('var, variable, actual, ')
    variable, args, kwargs = extractArg(Any, variableKeys, *args, **kwargs)
    infoKeys = stringList('info, msg, note')
    info, args, kwargs = extractArg(str, infoKeys, *args, **kwargs)
    msg = """Expected variable %s to be of type %s but received %s!"""
    if info is not None:
      self._msg = '\n'.join([msg % (name, type_, variable), info])
    self._msg = msg % (name, type_, variable)
    return self._msg
