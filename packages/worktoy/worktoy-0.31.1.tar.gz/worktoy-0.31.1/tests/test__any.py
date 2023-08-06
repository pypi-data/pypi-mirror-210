#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest
from worktoy.typetools import Any


class AnyTestCase(unittest.TestCase):
  def test_instance_check(self):
    # Test instance check
    self.assertTrue(isinstance(1, Any))
    self.assertTrue(isinstance("hello", Any))
    self.assertTrue(isinstance([1, 2, 3], Any))
    self.assertTrue(isinstance({'key': 'value'}, Any))
    self.assertTrue(isinstance((1, 2, 3), Any))

  def test_singleton_instance(self):
    # Test singleton instance
    a1 = Any()
    a2 = Any()
    self.assertIs(a1, a2)


if __name__ == '__main__':
  unittest.main()
