"""ExceptionCore provides a central baseclass for exceptions shared by
modules. This allows for general adjustments that apply to the entire
package as well as module specific error handling."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import sys

from icecream import ic

from worktoy.stringtools import justify

ic.configureOutput(includeContext=True)


class ExceptionCore(Exception, ):
  """ExceptionCore implements basic error/warning functionality. To set a
  Custom message, reimplement the _createMsg method.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""

  @staticmethod
  def _getHeader() -> str:
    """Getter-function for the header line"""
    return 77 * '_'

  @staticmethod
  def _getFooter() -> str:
    """Getter-function for footer line"""
    return 77 * '¨'

  def __init__(self, *args, **kwargs) -> None:
    self._msg = None
    if 'unittest' not in sys.argv[0]:
      self._createMsg(*args, **kwargs)
      print(self._getHeader())
      for line in justify(self._getMsg()).split('\n'):
        print(line)
      print(self._getFooter())
    Exception.__init__(self, )

  def _createMsg(self, *args, **kwargs) -> str:
    """This method creates the message displayed. Reimplement in subclass."""
    self._msg = Exception.__str__(self)
    return self._msg

  def _getMsg(self) -> str:
    """Getter-function for message"""
    return self._msg
