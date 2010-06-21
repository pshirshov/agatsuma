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
from mp_core import MPCore

__all__ = ["Core",
           "MPCore",
           ]
