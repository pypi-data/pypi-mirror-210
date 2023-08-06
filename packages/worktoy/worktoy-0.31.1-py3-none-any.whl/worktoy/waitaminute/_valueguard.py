"""The valueGuard function raises an error if a given argument is of the
correct type, but of improper value."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.typetools import Any

from worktoy.parsing import extractArg
from worktoy.stringtools import stringList
from worktoy.typetools import CallMeMaybe


def valueGuard(test: Any, *args, **kwargs) -> Any:
  """The valueGuard function raises an error if a given argument is of the
  correct type, but of improper value.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""
  valKeys = stringList('validator, discriminator, domain')
  validator, a, k = extractArg(CallMeMaybe, valKeys, *args, **kwargs)
  errorKeys = stringList('e, msg, error, exception, ')
  errorMsg, a, k = extractArg(str, errorKeys, *a, **k)
  if validator(test):
    return test
  raise ValueError(errorMsg)
