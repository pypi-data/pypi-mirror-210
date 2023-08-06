"""The extractArg function collects an argument from args and kwargs and
returns a tuple with the extracted argument and the remaining args and
kwargs. For example:
  myType: type
  myKeys: tuple[str]
  myArg, newArgs, newKwargs = extractArg(myType, myKeys, *args, **kwargs)
"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.typetools import TypeBag, Any

EXTRACTED = tuple[Any, list, dict]
KEYS = TypeBag(tuple[str, ...], list[str], str)


def extractArg(type_: type, keys: KEYS, *args, **kwargs) -> EXTRACTED:
  """The extractArg function collects an argument from args and kwargs and
  returns a tuple with the extracted argument and the remaining args and
  kwargs. For example:
    myType: type
    myKeys: tuple[str]
    myArg, newArgs, newKwargs = extractArg(myType, myKeys, *args, **kwargs)
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""
  if isinstance(keys, str):
    keys = [keys, ]
  out = None
  newArgs, newKwargs = [], {}
  for (key, val) in kwargs.items():
    if key in keys and isinstance(val, type_) and out is None:
      out = val
    else:
      newKwargs |= {key: val}
  for item in args:
    if out is None:
      if type_ == Any:
        out = item
      elif isinstance(item, type_):
        out = item
    else:
      newArgs.append(item)
  return (out, newArgs, newKwargs)
