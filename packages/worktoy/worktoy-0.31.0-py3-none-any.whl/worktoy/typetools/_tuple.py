"""Tuple represents a tuple of types"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from typing import Any
import typing

import _collections_abc

from icecream import ic

FakeTuple = getattr(typing, '_BaseGenericAlias')
iterable = getattr(_collections_abc, 'Iterable')

ic.configureOutput(includeContext=True)


class Tuple(FakeTuple, _root='F... tha police'):
  """Tuple represents a tuple of types
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  __type_like__ = True
  __name__ = 'tuple'
  __qualname__ = 'tuple'
  _subClasses = []

  @staticmethod
  def collectTypes(*types) -> list[type]:
    """Collects types or type like objects"""
    out = []
    for type_ in [*types, ]:
      if isinstance(type_, type) or getattr(type_, '__type_like__', False):
        out.append(type_)
    return out

  @classmethod
  def __init_subclass__(cls, **kwargs) -> Any:
    """LOL"""
    Tuple._subClasses.append(cls)

  def __init__(self, *types) -> None:
    self.origin = iterable
    self._containers = [list, tuple, ]
    name = getattr(self, '__name__', 'lol')
    FakeTuple.__init__(self, tuple, inst=True, name=None)
    self._baseTypes = self.collectTypes(*types)
    self._inst = True
    setattr(self.origin, '__name__', 'tuple')
    self.__name__ = 'tuple'
    self.__qualname__ = 'tuple'

  @classmethod
  def __subclasscheck__(cls, other: type) -> bool:
    """LOL"""
    return True if other in cls._subClasses else False

  def __getattr__(self, attr: Any) -> Any:
    """LOL"""
    if attr == '__origin__' or 'origin':
      return iterable
    if attr == '__name__':
      return self.__name__
    raise AttributeError(attr)

  def __setattr__(self, attr, val) -> typing.NoReturn:
    """omg"""
    object.__setattr__(self, attr, val)

  def __instancecheck__(self, instance: Any) -> bool:
    """Instance check. Instance must be a tuple, and its contents must
    match type types in the tuple."""
    if not isinstance(instance, (*self._containers,)):
      return False
    instance = [*instance, ]
    if len(self._baseTypes) != len(instance):
      return False
    for (obj, type_) in zip(instance, self._baseTypes):
      if not isinstance(obj, type_):
        return False
    return True

  def __str__(self) -> str:
    """String Representation"""
    typeNames = ['%s' % type_.__name__ for type_ in self._baseTypes]
    return """Tuple of types: %s""" % (', '.join(typeNames))
