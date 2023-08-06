"""The justify function works similarly to monoSpace, except for ignoring
all new-line indicators and instead splits the string into lines separated
by new-line at given intervals. """
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from worktoy.core import maybe
from worktoy.stringtools import monoSpace


def justify(text: str, charLimit: int = None, *spaceLike: str) -> str:
  """The justify function works similarly to monoSpace, except for ignoring
  all new-line indicators and instead splits the string into lines separated
  by new-line at given intervals.
  #  MIT License
  #  Copyright (c) 2023 Asger Jon Vistisen"""
  if not text:
    return ''
  text = text.replace(' %', '¤¤')
  text = monoSpace(text)
  charLimit = maybe(charLimit, 77)
  spaceLike = [' ', *spaceLike]
  allWords = [text.split(space) for space in spaceLike]
  wordList = []
  for words in allWords:
    wordList = [*wordList, *words]
  words = wordList
  lines = []
  line = []
  for (i, word) in enumerate(words):
    if sum([len(w) for w in line]) + len(word) + len(line) + 1 < charLimit:
      line.append(word)
    else:
      lines.append(line)
      line = [word, ]
  lines.append(line)
  lineList = []
  for line in lines:
    lineList.append(' '.join(line))
  out = '\n'.join(lineList)
  out = out.replace('¤¤', ' %')
  return out
