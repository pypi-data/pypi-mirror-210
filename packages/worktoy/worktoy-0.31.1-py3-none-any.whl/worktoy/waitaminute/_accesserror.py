"""AccessError is similar to AttributeError. It should receive the object
and name where name failed to correspond to an attribute on object."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.typetools import Any

from worktoy.parsing import extractArg
from worktoy.stringtools import stringList
from worktoy.waitaminute import ExceptionCore


class AccessError(ExceptionCore):
  """AccessError is similar to AttributeError. It should receive the object
  and name where name failed to correspond to an attribute on object.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    nameKeys = stringList('name, varName, var, ')
    name, args, kwargs = extractArg(str, nameKeys, *args, **kwargs)
    objKeys = stringList('object, obj, instance, item')
    obj, args, kwargs = extractArg(Any, objKeys, *args, **kwargs)
    msg = """Instance %s of type %s does not recognize key named %s!"""
    self._msg = msg % (obj, type(obj), name)
    return self._msg
