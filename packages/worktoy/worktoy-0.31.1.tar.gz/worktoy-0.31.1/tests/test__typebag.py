#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest
from typing import Union
from worktoy.core import maybe
from worktoy.typetools import TypeBag


class TypeBagTests(unittest.TestCase):

  def test_instance_check(self):
    bag = TypeBag(int, float, complex, str)
    self.assertTrue(isinstance(10, bag))
    self.assertTrue(isinstance("hello", bag))
    self.assertTrue(isinstance(3.14, bag))
    self.assertFalse(isinstance(True, bag))

  def test_str_representation(self):
    bag = TypeBag(int, float, complex, str)
    self.assertEqual(str(bag),
                     "Union of the following types: int, float, complex, "
                     "str")

  def test_code_representation(self):
    bag = TypeBag(int, float, complex, str)
    self.assertEqual(repr(bag), "TypeBag(int, float, complex, str)")

  def test_union_with_special_types(self):
    bag = TypeBag(int, float, complex)
    self.assertTrue(isinstance(10, bag))
    self.assertTrue(isinstance(3.14, bag))
    self.assertTrue(isinstance(2 + 3j, bag))
    self.assertFalse(isinstance(True, bag))
    self.assertFalse(isinstance("hello", bag))
    self.assertFalse(isinstance([1, 2, 3], bag))

  def test_custom_name(self):
    bag = TypeBag(int, float, complex, str, name="MyBag")
    self.assertEqual(str(bag),
                     "Union of the following types: int, float, complex, "
                     "str")
    self.assertEqual(bag.__name__, "MyBag")


if __name__ == '__main__':
  unittest.main()
