"""CallMeMaybe represents callable types."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import typing
from typing import NoReturn

from icecream import ic

from worktoy.typetools import Any

_HereIsMyNumber = getattr(typing, '_GenericAlias', None)

ic.configureOutput(includeContext=True)


class HereIsMyNumber(_HereIsMyNumber, _root='F... tha police!'):
  """Breaking into typing"""

  __type_like__ = True

  def __init__(self) -> None:
    pass

  @classmethod
  def __init_subclass__(cls, /, *args, **kwargs) -> NoReturn:
    """ClassFail"""

  @classmethod
  def __instancecheck__(cls, instance: Any) -> bool:
    """The top parent class should not take domain and range into account."""
    if instance is None:
      return False
    insCls = getattr(instance, '__class__', None)
    if insCls is None:
      from worktoy.waitaminute import UnexpectedStateError
      raise UnexpectedStateError(insCls)
    names = [getattr(insCls, key, None) for key in ['name', 'qualname']]
    from worktoy.core import empty
    if empty(names):
      from worktoy.waitaminute import UnexpectedStateError
      raise UnexpectedStateError(names)
    if any([n in names for n in ['function', 'method']]):
      return True
    call = getattr(insCls, '__call__', None)
    if call is None:
      return False
    return True

  def __str__(self, ) -> str:
    """String Representation"""
    return 'CallMeMaybe'

  def __repr__(self, ) -> str:
    """Code Representation"""
    return 'CallMeMaybe'


class _CallMeMaybe(HereIsMyNumber):
  """Subclassing to make singleton version"""
  _instance = None

  def __new__(cls) -> _CallMeMaybe:
    """Ensures that only one instance will exist"""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def __call__(self) -> type:
    """Just returns self"""
    return self

  def __str__(self, ) -> str:
    """String Representation"""
    return 'CallMeMaybe'

  def __repr__(self, ) -> str:
    """Code Representation"""
    return 'CallMeMaybe'


CallMeMaybe = _CallMeMaybe()
