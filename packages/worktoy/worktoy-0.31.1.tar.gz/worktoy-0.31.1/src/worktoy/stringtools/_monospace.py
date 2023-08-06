"""Documentation: monoSpace
Convert text to monospaced format with consistent spacing and line
  breaks."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.core import maybe


def monoSpace(text: str, newLine: str = None) -> str:
  """Convert text to monospaced format with consistent spacing and line
  breaks.

  Args:
    text (str): The input text to be modified.
    newLine (str, optional):
      The string representing the line break. If not provided,
      the default value '<br>' is used. Defaults to None.

  Returns:
    str: The modified text with consistent spacing and line breaks.

  Raises:
    None

  Examples:
    >>> monoSpace('Hello   World!')
    'Hello World!'
    >>> monoSpace('Hello<br>World!', '<br>')
    'Hello\nWorld!'

  The `monoSpace` function takes a string `text` and an optional string
  `newLine`, and returns a modified version of the input text with consistent
  spacing and line breaks. If the `newLine` argument is not provided, the
  default value '<br>' is used as the line break string.

  The function performs the following steps:
  1. Replaces all occurrences of '\n' and '\r' characters with a space ' ' in
     the input `text`.
  2. Repeatedly replaces multiple consecutive spaces with a single space
     until no more consecutive spaces are found in the `text`.
  3. Replaces the `newLine` string (or the default '<br>' if not provided)
     with a line break '\n' character in the modified `text`.
  4. Returns the modified `text`.

  Note:
  - The `newLine` string is treated as a literal string, so make sure to
    provide the exact string to be replaced as the line break.
  - The `newLine` string is case-sensitive. If the provided `newLine` string
    does not match the exact case in the input `text`, it will not be
    replaced with a line break."""
  newLine = maybe(newLine, '<br>')
  text = text.replace('\n', ' ').replace('\r', ' ')
  while '  ' in text:
    text = text.replace('  ', ' ')
  return text.replace(newLine, '\n')
