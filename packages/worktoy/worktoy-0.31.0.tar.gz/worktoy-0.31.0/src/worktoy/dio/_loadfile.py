"""The loadFile function loads a file at a given path with comprehensive
error handling."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.waitaminute import DIOError


def loadFile(file_path: str) -> str:
  """The loadFile function loads a file at a given path with comprehensive
  error handling.
  #  Copyright (c) 2023 Asger Jon Vistisen
  #  MIT Licence"""
  errorMsg = None
  try:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    except FileNotFoundError as noFile:
      errorMsg = 'Unable to locate file!'
      raise noFile
    except PermissionError as noAccess:
      errorMsg = 'Access to file denied!'
      raise noAccess
    except IsADirectoryError as isDir:
      e = """The path: %s specifies a directory, not a file"""
      errorMsg = e % file_path
      raise isDir
    except UnicodeDecodeError as decodeError:
      errorMsg = 'While reading the file encountered decoding error!'
      raise decodeError
    except IOError as other:
      errorMsg = 'Encountered general input/output error!'
      raise other
    return content
  except Exception as e:
    raise DIOError(errorMsg) from e
