#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest
from worktoy.parsing import maybeType


class MaybeTypeTests(unittest.TestCase):

  def test_maybeType_no_args(self):
    result = maybeType(int)
    self.assertIsNone(result)

  def test_maybeType_single_arg_matching_type(self):
    result = maybeType(int, 1)
    self.assertEqual(result, 1)

  def test_maybeType_single_arg_not_matching_type(self):
    result = maybeType(int, "1")
    self.assertIsNone(result)

  def test_maybeType_multiple_args_with_matching_type(self):
    result = maybeType(int, 1, 2, 3, 4)
    self.assertEqual(result, 1)

  def test_maybeType_multiple_args_with_mixed_types(self):
    result = maybeType(int, 1, "2", 3, "4")
    self.assertEqual(result, 1)

  def test_maybeType_multiple_args_with_no_matching_type(self):
    result = maybeType(int, "1", "2", "3", "4")
    self.assertIsNone(result)

  def test_maybeType_multiple_args_with_none_values(self):
    result = maybeType(int, None, 1, None, 2)
    self.assertEqual(result, 1)

  def test_maybeType_multiple_args_with_all_none_values(self):
    result = maybeType(int, None, None, None)
    self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()
