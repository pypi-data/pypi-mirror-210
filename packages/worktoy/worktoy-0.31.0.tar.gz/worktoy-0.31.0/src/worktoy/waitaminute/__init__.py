"""A collection of custom exception using the 'inspect' module to collect
contextual information. This is achieved by the 'ExceptionCore' class. A
few subclasses are included, but users are invited to subclass
'ExceptionCore' as needed. On its own, ExceptionCore does nothing more
than the builtin Exception, but having a central baseclass allows for
future advancements to see quick implementation across the entire
collection of exceptions.

Future:
Proposed developments of this module:
 - Enhance the capabilities of ExceptionCore to automatically collect
relevant information.
 - Create a richer and stronger type guard system.
"""
#  Copyright (c) 2023 Asger Jon Vistisen
#  MIT Licence
from __future__ import annotations

from ._exceptioncore import ExceptionCore
from ._instantiationerror import InstantiationError
from ._unexpectedstateerror import UnexpectedStateError
from ._validationerror import ValidationError
from ._accesserror import AccessError
from ._manualinterrupt import ManualInterrupt
from ._proceduralerror import ProceduralError
from ._dioerror import DIOError
from ._typeguarderror import TypeGuardError
from ._n00berror import n00bError
from ._valueguard import valueGuard
from ._readonlyerror import ReadOnlyError
