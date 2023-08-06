"""TypeBag is a subclass of the typing union classes that support
isinstance."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import typing
from worktoy.typetools import Any
import collections.abc

from icecream import ic

from worktoy.core import maybe

union = getattr(typing, '_UnionGenericAlias', None)
if union is None:
  raise ImportError('Failed to find _UnionGenericAlias!')

ic.configureOutput(includeContext=True)

UnionType = getattr(typing, '_BaseGenericAlias')
ContainerType = getattr(collections.abc, 'Container')


class TypeBag(UnionType, _root='F... tha police!'):
  """Alternative to Union"""

  __type_like__ = True
  _subClasses = []

  @classmethod
  def __init_subclass__(cls, **kwargs) -> Any:
    """LOL"""
    TypeBag._subClasses.append(cls)

  def __init__(self, *types, **kwargs) -> None:
    if not kwargs.get('_special', False):
      newTypes = []
      for type_ in types:
        if type_ in [int, float, complex]:
          if all([t not in newTypes for t in [int, float, complex]]):
            newTypes = [*newTypes, int, float, complex]
        elif isinstance(type_, type):
          newTypes.append(type_)
      types = newTypes
    self.__origin__ = ContainerType
    self._types = []
    name = kwargs.get('name', None)
    for type_ in [*types]:
      if isinstance(type_, type):
        self._types.append(type_)
      if isinstance(type_, str) and name is None:
        name = type_
    setattr(self, '__name__', maybe(name, 'Type'))
    UnionType.__init__(self, ContainerType)

  def __instancecheck__(self, obj) -> bool:
    if isinstance(obj, bool):
      if bool in self._types:
        return True
      return False
    for type_ in self._types:
      if isinstance(obj, type_):
        return True
    return False

  def __setattr__(self, key, value) -> typing.NoReturn:
    """Overwrite"""
    object.__setattr__(self, key, value)

  def __subclasscheck__(self, cls: type) -> bool:
    """LOL"""
    return True if cls in self._subClasses else False

  def __getattr__(self, attr: Any) -> Any:
    """LOL"""
    return getattr(self.__origin__, attr)

  def __str__(self) -> str:
    """String Representation"""
    typeNames = [type_.__name__ for type_ in self._types]
    msg = """Union of the following types: %s""" % (', '.join(typeNames))
    return msg

  def __repr__(self) -> str:
    """Code representation"""
    typeNames = [type_.__name__ for type_ in self._types]
    return 'TypeBag(%s)' % ', '.join(typeNames)


Numerical = TypeBag(int, float, complex, )
