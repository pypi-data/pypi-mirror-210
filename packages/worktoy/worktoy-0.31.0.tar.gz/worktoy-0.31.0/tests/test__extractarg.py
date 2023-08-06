"""Testing ExtractArg"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from unittest import TestCase

from worktoy.parsing import extractArg
from worktoy.typetools import Any


class TestExtractArg(TestCase):
  def test_extract_arg_with_positional_argument(self):
    # Tests that a positional argument is correctly extracted.
    my_arg, new_args, new_kwargs = extractArg(str, ["my_arg"], "hello")
    self.assertEqual(my_arg, "hello")
    self.assertEqual(new_args, [])
    self.assertEqual(new_kwargs, {})

  def test_extract_arg_with_keyword_argument(self):
    # Tests that a keyword argument is correctly extracted.
    my_arg, new_args, new_kwargs = extractArg(str, ["my_arg"],
                                              my_arg="world")
    self.assertEqual(my_arg, "world")
    self.assertEqual(new_args, [])
    self.assertEqual(new_kwargs, {})

  def test_extract_arg_with_multiple_arguments(self):
    # Tests that the first matching argument is correctly extracted.
    my_arg, new_args, new_kwargs = extractArg(str, ["my_arg"], "hello",
                                              "world", my_arg="universe")
    self.assertEqual(my_arg, "universe")
    self.assertEqual(new_args, ["hello", "world"])
    self.assertEqual(new_kwargs, {})

  def test_extract_arg_with_no_matching_argument(self):
    # Tests that None is returned when no argument matches the criteria.
    my_arg, new_args, new_kwargs = extractArg(str, ["my_arg"],
                                              some_arg="value")
    self.assertIsNone(my_arg)
    self.assertEqual(new_args, [])
    self.assertEqual(new_kwargs, {"some_arg": "value"})

  def test_extract_arg_with_any_type(self):
    # Tests that Any type matches any argument.
    my_arg, new_args, new_kwargs = extractArg(Any, ["some_arg"],
                                              some_arg="value")
    self.assertEqual(my_arg, "value")
    self.assertEqual(new_args, [])
    self.assertEqual(new_kwargs, {})

  def test_extract_arg_with_single_key(self):
    # Tests that the keys parameter can be a single string.
    my_arg, new_args, new_kwargs = extractArg(str, "my_arg", my_arg="hello")
    self.assertEqual(my_arg, "hello")
    self.assertEqual(new_args, [])
    self.assertEqual(new_kwargs, {})
