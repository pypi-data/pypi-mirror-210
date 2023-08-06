"""BaseField decorates classes with fields"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations
from typing import Any, NoReturn

from icecream import ic

from worktoy.core import maybe
from worktoy.parsing import searchKeys
from worktoy.stringtools import stringList
from worktoy.waitaminute import ReadOnlyError, ProceduralError

ic.configureOutput(includeContext=True)


class BaseField:
  """field decorates a class a with a field
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""

  def __init__(self, name: str, value: Any, **kwargs) -> None:
    self._name = name
    self._value = value
    self._defVal = value
    typeArg = None if self._value is None else type(self._value)
    readOnlyKeys = stringList('readOnly, noSet, lock, writeProtect')
    readOnly = searchKeys(*readOnlyKeys) @ bool >> kwargs
    self._readOnly = True if readOnly else False
    typeKeys = stringList('type, type_, class, class_')
    typeKwarg = searchKeys(typeKeys) >> kwargs
    self._type = maybe(typeArg, typeKwarg, None)
    if self._type is None:
      raise ProceduralError('_type', type, None)
    self._owner = None
    self._instance = None

  def __get__(self, *args) -> Any:
    """Implementation of getter"""
    return self._value

  def __set__(self, *args, ) -> NoReturn:
    """Implementation of setter"""
    if self._readOnly:
      raise ReadOnlyError.Field(self)
    if self._instance is None:
      self._instance = args[0]
    self._value = args[1]

  def __call__(self, cls: type) -> type:
    """Decorates the class"""
    fields = getattr(cls, '__fields__', None)
    if fields is None:
      fields = {}
    fields |= {self.getName(): self}
    setattr(cls, '__fields__', fields)
    self._owner = cls
    setattr(cls, self._name, self)
    return cls

  def getName(self) -> str:
    """Getter-function for the name of the field"""
    return self._name

  def getOwner(self) -> type:
    """Getter-function for the owner class"""
    if self._owner is None:
      raise ProceduralError('_owner', type, None)
    return self._owner

  def getInstance(self, ) -> Any:
    """Getter-function for the owner instance"""
    return self._instance

  def __str__(self, ) -> str:
    """String Representation"""
    msg = """BaseField %s on class %s and instance %s."""
    return msg % (self.getName(), self.getOwner(), self.getInstance())

  def __repr__(self) -> str:
    """Code Representation"""
    className = self.__class__.__name__
    if self._readOnly:
      if self._defVal is None:
        msg = '%s(%s, type_=%s, readOnly=True)'
        return msg % (className, self.getName(), self._type)
      msg = """%s(%s, %s, readOnly=True)"""
      return msg % (className, self.getName(), self._defVal,)
    if self._defVal is None:
      return '%s(%s, type_=%s)' % (className, self.getName(), self._type)
    return '%s(%s, %s)' % (className, self.getName(), self._defVal)
