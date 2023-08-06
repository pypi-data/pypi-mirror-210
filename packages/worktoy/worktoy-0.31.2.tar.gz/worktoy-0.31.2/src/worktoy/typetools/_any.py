"""Any is any type"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations


class _AnyMeta(type):
  """A metaclass for implementing instance check"""

  @classmethod
  def __instancecheck__(mcls, obj) -> bool:
    return True


class _Any(metaclass=_AnyMeta):
  """Intermediary class"""
  pass

  __type_like__ = True


class Any(_Any):
  """Special type indicating an unconstrained type."""

  _instance = _Any()

  def __new__(cls, *args, **kwargs) -> _Any:
    """Simply returns the instance"""
    return cls._instance
