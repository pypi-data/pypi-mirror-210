"""The stringList function provides an easier way to write lists of
strings. Instead of wrapping each item in ticks, write on long string with
consistent separators, and stringList will convert it to a list of
strings.
Instead of: numbers = ['one', 'two', 'three', 'four']
Use stringList: numbers = stringList('one, two, three, four')"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.core import maybe
from worktoy.parsing import maybeTypes, searchKeys


def stringList(*args, **kwargs) -> list[str]:
  """The stringList function provides an easier way to write lists of
  strings. Instead of wrapping each item in ticks, write on long string with
  consistent separators, and stringList will convert it to a list of
  strings.
  Instead of: numbers = ['one', 'two', 'three', 'four']
  Use stringList: numbers = stringList('one, two, three, four')
  Please note that all white space around each separator will be removed.
  Meaning that ', ' and ',' will produce the same outcome when used as
  separators on the same text.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  strArgs = maybeTypes(str, *args, padLen=3, padChar=None)
  sourceKwarg = searchKeys('source', 'src', 'txt') @ str >> kwargs
  separatorKwarg = searchKeys('separator', 'splitHere') @ str >> kwargs
  sourceArg, separatorArg, ignoreArg = strArgs
  sourceDefault, separatorDefault = None, ', '
  source = maybe(sourceKwarg, sourceArg, sourceDefault)
  separator = maybe(separatorKwarg, separatorArg, separatorDefault, )
  if source is None:
    msg = 'stringList received no string!'
    raise ValueError(msg)
  out = source.split(separator)
  return out
