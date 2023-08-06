"""Documentation: ReadOnlyError"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import inspect
from typing import Never

from icecream import ic

from worktoy.core import maybe
from worktoy.parsing import searchKeys
from worktoy.stringtools import monoSpace
from worktoy.waitaminute import ExceptionCore

ic.configureOutput(includeContext=True)


class ReadOnlyError(ExceptionCore):
  """Custom exception for read-only operations."""

  @classmethod
  def Field(cls, Field) -> ReadOnlyError:
    """Creates an instance of read only error based on a field"""
    varName = Field.getName()
    ownerName = Field.getOwner()
    return ReadOnlyError(varName, ownerName, )

  @classmethod
  def yoDawg(cls) -> ExceptionCore:
    """Create an exception instance of ReadOnlyError."""
    msg = """Heard you like ReadOnlyError, so we put a ReadOnlyError
          in your ReadOnlyError!"""
    from worktoy.stringtools import monoSpace
    return ExceptionCore(monoSpace(msg))

  def __init__(self, *args, **kwargs) -> None:
    """Initialize the ReadOnlyError exception.
    Args:
        *args: Variable arguments.
        **kwargs: Keyword arguments.
    Raises:
        None
    Returns:
        None"""
    self._variableName = None
    self._function = None
    self._fileName = None
    self._lineNumber = None
    self._instance = None
    self._instanceClass = None
    ExceptionCore.__init__(self, *args, **kwargs)

  def _createMsg(self, *args, **kwargs) -> str:
    """Reimplementation"""
    args = [*args, None]
    variableKwarg = searchKeys('variable', 'var') @ str >> kwargs
    variableArg = args[0]
    self._variableName = maybe(variableKwarg, variableArg, None)
    frame = inspect.currentframe().f_back
    code = frame.f_code
    self._function = inspect.getframeinfo(frame).function
    self._fileName = code.co_filename
    self._lineNumber = frame.f_lineno
    self._instance = frame.f_locals.get('self', )
    self._instanceClass = type(self._instance)
    msg = "Tried to access %s belonging to %s of class %s using %s, " \
          "which is not a permitted operation!"
    self._msg = monoSpace(msg % (
      self.varName, self.insName, self.insCls, self.function))
    return self._msg

  def _getVariable(self) -> str:
    """Getter-function for the name of the variable.
    Returns:
        str: Name of the variable."""
    return maybe(self._variableName, 'unnamed')

  def _setVariable(self, *_) -> Never:
    """Illegal setter function.
    Args:
        *_: Variable arguments.
    Raises:
        ReadOnlyError: Always raised to indicate that setting the variable
        is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _delVariable(self) -> Never:
    """Illegal deleter function.
    Raises:
        ReadOnlyError: Always raised to indicate that deleting the
        variable is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _getFunction(self) -> str:
    """Getter-function for the function invoking the error.
    Returns:
        str: Name of the function."""
    return self._function

  def _setFunction(self, *_) -> Never:
    """Illegal setter function.
    Args:
        *_: Variable arguments.
    Raises:
        ReadOnlyError: Always raised to indicate that setting the function
        is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _delFunction(self) -> Never:
    """Illegal deleter function.
    Raises:
        ReadOnlyError: Always raised to indicate that deleting the
        function is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _getFileName(self) -> str:
    """Getter-function for the file name.
    Returns:
        str: File name."""
    return self._fileName

  def _setFileName(self, *_) -> Never:
    """Illegal setter function.
    Args:
        *_: Variable arguments.
    Raises:
        ReadOnlyError: Always raised to indicate that setting the file
        name is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _delFileName(self) -> Never:
    """Illegal deleter function.
    Raises:
        ReadOnlyError: Always raised to indicate that deleting the file
        name is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _getLineNumber(self) -> str:
    """Getter-function for the line number.
    Returns:
        str: Line number."""
    return self._lineNumber

  def _setLineNumber(self, *_) -> Never:
    """Illegal setter function.
    Args:
        *_: Variable arguments.
    Raises:
        ReadOnlyError: Always raised to indicate that setting the line
        number is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _delLineNumber(self) -> Never:
    """Illegal deleter function.
    Raises:
        ReadOnlyError: Always raised to indicate that deleting the line
        number is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _getInstance(self) -> str:
    """Getter-function for the instance.
    Returns:
        str: Instance name."""
    return maybe(self._instance, 'unnamed instance')

  def _setInstance(self, *_) -> Never:
    """Illegal setter function.
    Args:
        *_: Variable arguments.
    Raises:
        ReadOnlyError: Always raised to indicate that setting the instance
        is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _delInstance(self) -> Never:
    """Illegal deleter function.
    Raises:
        ReadOnlyError: Always raised to indicate that deleting the
        instance is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _getInstanceClass(self) -> str:
    """Getter-function for the instance class.
    Returns:
        str: Instance class name."""
    return maybe(self._instanceClass, 'unnamed class')

  def _setInstanceClass(self, *_) -> Never:
    """Illegal setter function.
    Args:
        *_: Variable arguments.
    Raises:
        ReadOnlyError: Always raised to indicate that setting the instance
        class is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  def _delInstanceClass(self) -> Never:
    """Illegal deleter function.
    Raises:
        ReadOnlyError: Always raised to indicate that deleting the
        instance class is not allowed.
    Returns:
        Never"""
    raise self.yoDawg()

  varName = property(_getVariable, _setVariable, _delVariable)
  function = property(_getFunction, _setFunction, _delFunction)
  fileName = property(_getFileName, _setFileName, _delFileName)
  lineNumber = property(_getLineNumber, _setLineNumber, _delLineNumber)
  insName = property(_getInstance, _setInstance, _delInstance)
  insCls = property(_getInstanceClass, _setInstanceClass, _delInstanceClass)
