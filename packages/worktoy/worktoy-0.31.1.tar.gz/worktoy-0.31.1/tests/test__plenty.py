#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest

from worktoy.core import plenty


class TestPlenty(unittest.TestCase):
  def test_plenty_with_one_argument(self):
    self.assertTrue(plenty(1))
    self.assertTrue(plenty("hello"))
    self.assertFalse(plenty(None))

  def test_plenty_with_multiple_arguments(self):
    self.assertTrue(plenty(1, "hello", [1, 2, 3]))
    self.assertFalse(plenty(1, None, [1, 2, 3]))
    self.assertFalse(plenty(None, None, None))


if __name__ == '__main__':
  unittest.main()
