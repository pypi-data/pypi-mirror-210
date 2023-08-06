"""Testing CallMeMaybe"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

import unittest
from typing import NoReturn

from icecream import ic

from worktoy.typetools import CallMeMaybe

ic.configureOutput(includeContext=True)


class TestCallMeMaybe(unittest.TestCase):

  def testSingleton(self) -> NoReturn:
    """Testing"""
    cm1 = CallMeMaybe()
    cm2 = CallMeMaybe()
    self.assertIs(cm1, cm2)

  def testCall(self) -> NoReturn:
    """Testing"""
    cm = CallMeMaybe()
    self.assertIs(cm(), cm)

  def testStr(self) -> NoReturn:
    """Testing"""
    cm = CallMeMaybe()
    self.assertEqual(str(cm), "CallMeMaybe")

  def test_repr(self) -> NoReturn:
    """Testing"""
    cm = CallMeMaybe()
    self.assertEqual(repr(cm), "CallMeMaybe")

  def test_instancecheck_no_class(self) -> NoReturn:
    """Testing"""
    cm = CallMeMaybe
    self.assertFalse(isinstance(None, cm))

  def test_instancecheck_function(self) -> NoReturn:
    """Testing"""

    def func() -> NoReturn:
      """Testing"""
      pass

    cm = CallMeMaybe
    self.assertIsInstance(func, cm)
    # self.assertTrue(isinstance(func, cm))

  def test_instancecheck_method(self) -> NoReturn:
    """Testing"""

    class MyClass:
      """Testing"""

      def method(self) -> NoReturn:
        """Testing"""
        pass

    cm = CallMeMaybe
    self.assertIsInstance(MyClass().method, cm)
