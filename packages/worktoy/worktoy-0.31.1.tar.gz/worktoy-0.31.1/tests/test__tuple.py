#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest

from worktoy.typetools import Tuple


class TupleTestCase(unittest.TestCase):
  def test_collect_types(self):
    # Test collecting types
    t1 = Tuple.collectTypes(int, str, float)
    self.assertEqual(t1, [int, str, float])

  def test_instance_check(self):
    # Test instance check
    t = Tuple(int, str)
    self.assertTrue(isinstance((1, 'hello'), t))
    self.assertTrue(isinstance([1, 'hello'], t))
    self.assertFalse(isinstance([1, 2], t))
    self.assertFalse(isinstance((1,), t))

  def test_string_representation(self):
    # Test string representation
    t1 = Tuple(int, str, float)
    self.assertEqual(str(t1), "Tuple of types: int, str, float")

    t2 = Tuple(int)
    self.assertEqual(str(t2), "Tuple of types: int")
