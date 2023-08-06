"""The parsing module provides functionalities relating to parsing of
arguments. Central is the parse function which implements a combined type
and keyword search."""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from ._maybetype import maybeType
from ._searchkeys import searchKeys
from ._maybetypes import maybeTypes
from ._extractarg import extractArg
