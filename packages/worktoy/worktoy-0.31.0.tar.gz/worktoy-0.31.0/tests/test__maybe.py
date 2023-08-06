#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from random import shuffle
from typing import NoReturn
from unittest import TestCase

from worktoy.core import maybe


class TestMaybe(TestCase):
  """Testing the 'maybe' function"""

  def setUp(self) -> NoReturn:
    """Setting up each test"""
    self.someFalse = [0, 0j, False, dict(), set(), tuple(), list(), '']

  def testNoArgs(self) -> NoReturn:
    """Testing the case with no arguments"""
    self.assertIsNone(maybe())

  def testingEach(self) -> NoReturn:
    """For each type in someFalse, we check if is extracted from a pile of
    None"""
    pile = [None for _ in range(255)]
    for val in self.someFalse:
      draw = [*pile, val]
      shuffle(draw)
      self.assertIsInstance(maybe(*draw), type(val))
