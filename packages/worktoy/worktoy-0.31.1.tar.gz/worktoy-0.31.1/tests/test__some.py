"""Testing some"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from random import choices
from typing import NoReturn
from unittest import TestCase

from worktoy.core import some


class TestSome(TestCase):

  def setUp(self) -> NoReturn:
    """Sets up each test"""
    self.bag = [*[None] * 56, *[1] * 8]

  def testEmpty(self) -> NoReturn:
    """Testing empty"""
    draw = choices(self.bag, k=4)
    groundTruth = sum([1 for v in draw if v is not None])
    if groundTruth:
      self.assertTrue(some(*draw))
    else:
      self.assertFalse(some(*draw))
