#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest
from worktoy.parsing import maybeTypes


class MaybeTypesTests(unittest.TestCase):

  def test_maybeTypes_no_args(self):
    result = maybeTypes(int)
    self.assertEqual(result, [])

  def test_maybeTypes_single_arg_matching_type(self):
    result = maybeTypes(int, 1)
    self.assertEqual(result, [1])

  def test_maybeTypes_single_arg_not_matching_type(self):
    result = maybeTypes(int, "1")
    self.assertEqual(result, [])

  def test_maybeTypes_multiple_args_with_matching_type(self):
    result = maybeTypes(int, 1, 2, 3, 4)
    self.assertEqual(result, [1, 2, 3, 4])

  def test_maybeTypes_multiple_args_with_mixed_types(self):
    result = maybeTypes(int, 1, "2", 3, "4")
    self.assertEqual(result, [1, 3])

  def test_maybeTypes_kwargs_padLen_equal_length(self):
    kwargs = {'padLen': 3}
    result = maybeTypes(int, 1, 2, 3, **kwargs)
    self.assertEqual(result, [1, 2, 3])

  def test_maybeTypes_kwargs_padLen_less_than_length(self):
    kwargs = {'padLen': 2}
    result = maybeTypes(int, 1, 2, 3, **kwargs)
    self.assertEqual(result, [1, 2])

  def test_maybeTypes_kwargs_padLen_greater_than_length(self):
    kwargs = {'padLen': 5}
    result = maybeTypes(int, 1, 2, 3, **kwargs)
    self.assertEqual(result, [1, 2, 3, None, None])

  def test_maybeTypes_kwargs_padLen_and_padChar(self):
    kwargs = {'padLen': 4, 'padChar': 'x'}
    result = maybeTypes(int, 1, 2, 3, **kwargs)
    self.assertEqual(result, [1, 2, 3, 'x'])


if __name__ == '__main__':
  unittest.main()
