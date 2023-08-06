"""Testing the BaseField"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from enum import IntEnum
from random import randint
from typing import NoReturn
from unittest import TestCase

from PySide6.QtCore import QRect, QPoint

from worktoy.field import BaseField
from worktoy.waitaminute import ReadOnlyError


class Letter(IntEnum):
  """Some Letters"""
  A = 0
  B = 1
  C = 2


@BaseField('point', QPoint(1, 1), readOnly=True)
@BaseField('letter', Letter.A)
@BaseField('dictionary', {})
@BaseField('stuff', [])
@BaseField('Name', 'John Doe')
@BaseField('Height', 2)
@BaseField('Length', 5)
class Sample:
  """I am a sample class!"""

  def __init__(self, *args, **kwarg) -> None:
    pass


class TestBaseField(TestCase):
  """Testing BaseField"""

  def setUp(self) -> NoReturn:
    """Setting up each test"""
    self.sample = Sample()

  def testGetter(self) -> NoReturn:
    """Testing getter and initialisation """
    self.assertEqual(self.sample.Length, 5)
    self.assertEqual(self.sample.Height, 2)
    self.assertEqual(self.sample.Name, 'John Doe')
    self.assertFalse(self.sample.stuff)
    self.assertFalse(self.sample.dictionary)
    self.assertIsNotNone(self.sample.letter.A)
    self.assertIsInstance(self.sample.point, QPoint)

  def testSetter(self) -> NoReturn:
    """Testing setter"""
    num = randint(0, 255)
    self.sample.Length = num
    self.assertEqual(self.sample.Length, num)
    num = randint(0, 255)
    self.sample.Height = num
    self.assertEqual(self.sample.Height, num)
    self.sample.Name = 'lol'
    self.assertEqual(self.sample.Name, 'lol')

  def testString(self) -> NoReturn:
    """Testing if other types are supported such as string"""
    self.assertIsInstance(self.sample.Length, int)
    self.assertIsInstance(self.sample.Name, str)

  def testOperators(self) -> NoReturn:
    """Testing if += and other in-place operators work"""
    self.sample.Length = 2
    self.sample.Length += 2
    self.assertEqual(self.sample.Length, 4)
    self.sample.Length += 2
    self.assertEqual(self.sample.Length, 6)
    self.sample.Length *= 2
    self.assertEqual(self.sample.Length, 12)
    self.sample.Length -= 2
    self.assertEqual(self.sample.Length, 10)
    self.sample.Length /= 2
    self.assertEqual(self.sample.Length, 5)
    self.sample.Length **= 2
    self.assertEqual(self.sample.Length, 25)
    self.sample.Length %= 6
    self.assertEqual(self.sample.Length, 1)
    self.sample.Name = 'A'
    self.sample.Name += 'B'
    self.assertEqual(self.sample.Name, 'AB')

  def testingContainerAppends(self) -> NoReturn:
    """Test appends"""
    self.sample.stuff.append(1)
    self.assertTrue(self.sample.stuff)
    self.assertEqual(len(self.sample.stuff), 1)
    self.sample.dictionary['test'] = 77
    self.sample.dictionary['blabla'] = 777
    values = sorted([v for (k, v) in self.sample.dictionary.items()])
    self.assertListEqual([77, 777], values)

  def testingEnumFields(self) -> NoReturn:
    """Testing the enums"""
    self.assertIsNotNone(self.sample.letter)
    self.assertEqual(self.sample.letter, Letter.A)
    self.sample.letter = Letter.B
    self.assertEqual(self.sample.letter, Letter.B)

  def testingReadOnly(self) -> NoReturn:
    """Testing read only exceptions"""
    with self.assertRaises(ReadOnlyError):
      self.sample.point = QPoint(7, 7)
