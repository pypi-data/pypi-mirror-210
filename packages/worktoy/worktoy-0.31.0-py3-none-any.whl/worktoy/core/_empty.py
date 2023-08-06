"""Documentation - Empty
The objective of the 'empty' function is to determine whether all the
input arguments are None or not. If all the arguments are None,
the function returns True, otherwise, it returns False.

Inputs:
The 'empty' function takes in any number of arguments.

Flow:
The 'empty' function iterates through all the input arguments using a for
loop. For each argument, it checks if it is not None using an 'if'
statement. If an argument is not None, the function immediately returns
False. If all the arguments are None, the function returns True.

Outputs:
The 'empty' function returns a boolean value, either True or False.

Additional aspects:
The 'empty' function is licensed under the MIT License and was created by
Asger Jon Vistisen in 2023."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations


def empty(*args) -> bool:
  """The empty function returns True if all args are None. If even one is
  not None, False is returned
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  for arg in args:
    if arg is not None:
      return False
  return True
