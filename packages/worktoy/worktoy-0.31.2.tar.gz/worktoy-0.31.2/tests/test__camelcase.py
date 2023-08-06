#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence

import unittest
from worktoy.stringtools import snakeCaseToCamelCase


class SnakeCaseToCamelCaseTestCase(unittest.TestCase):
  def test_snake_case_to_camel_case(self):
    # Test conversion from snake_case to camelCase
    self.assertEqual(snakeCaseToCamelCase('hello_world'), 'helloWorld')
    self.assertEqual(snakeCaseToCamelCase('my_variable_name'),
                     'myVariableName')
    self.assertEqual(snakeCaseToCamelCase('convert_to_camel_case'),
                     'convertToCamelCase')
    self.assertEqual(snakeCaseToCamelCase('_leading_underscore'),
                     'LeadingUnderscore')
    self.assertEqual(snakeCaseToCamelCase('trailing_underscore_'),
                     'trailingUnderscore')

  def test_no_conversion_needed(self):
    # Test when no conversion is needed
    self.assertEqual(snakeCaseToCamelCase('camelCase'), 'camelCase')
    self.assertEqual(snakeCaseToCamelCase('alreadyCamelCase'),
                     'alreadyCamelCase')
    self.assertEqual(snakeCaseToCamelCase('no_underscores'), 'noUnderscores')


if __name__ == '__main__':
  unittest.main()
