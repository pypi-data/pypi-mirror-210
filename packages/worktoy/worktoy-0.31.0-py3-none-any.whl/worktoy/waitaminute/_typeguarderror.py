"""TypeGuardError is raised by the typeGuard function when a test object
fails the type guard check."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.waitaminute import ExceptionCore


class TypeGuardError(ExceptionCore):
  """TypeGuardError is raised by the typeGuard function when a test object
  fails the type guard check.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def __init__(self, *args, **kwargs) -> None:
    ExceptionCore.__init__(self, *args, **kwargs)

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    testArg = args[0]
    msg = """The test object %s is of type %s, which is not one of the 
    allowed types listed below: """ % (testArg, type(testArg))
    types = [msg, *['%s' % type_ for type_ in args[1:]]]
    return '\n'.join(types)
