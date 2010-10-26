# -*- coding: utf-8 -*-

"""
This package contains standard cores that may be used in
any application which needs to has extremal modularity.

Agatsuma Base Core
================================

.. autoclass:: agatsuma.core.Core
   :members:

Agatsuma Multiprocessing Core
================================

.. autoclass:: agatsuma.core.MPCore
   :members:

"""

from base_core import Core
from mp_core import MultiprocessingCoreExtension
from mp_core import MPStandaloneExtension

__all__ = ["Core",
           "MultiprocessingCoreExtension",
           "MPStandaloneExtension"
           ]
