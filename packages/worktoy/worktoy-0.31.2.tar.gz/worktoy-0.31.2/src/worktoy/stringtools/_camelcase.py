"""Transforms strings from snake_case to camelCase"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations
from re import Match, sub


def snakeCaseToCamelCase(string: str) -> str:
  """Replaces all instances of snake_case with camelCase in a given string.
  Args:

      string (str): The input string containing snake_case.
  Returns:
      str: The resulting string with snake_case replaced by camelCase."""

  string = string.replace('_ ', ' ')
  if string[-1] in ['_', ' ']:
    return snakeCaseToCamelCase(string[:-1])

  def camelCase(match: Match) -> str:
    """Convert snake_case match to camelCase"""
    word = match.group(1)
    return word[0].upper() + word[1:] if word else ""

  pattern = r'_(\w)'
  result = sub(pattern, camelCase, string)

  return result
