# -*- coding: utf-8 -*-
"""
This package contains interfaces and mix-ins that not depends from
any web framework and mostly even not related to web development.

Spells and spell mix-ins
************************

Base core interfaces
====================

.. autoclass:: agatsuma.interfaces.AbstractSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.ISetupSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.IFilteringSpell
   :members:
   :inherited-members:


Multiprocessing core interfaces
===============================

.. autoclass:: agatsuma.interfaces.IPoolEventSpell
   :members:
   :inherited-members:


Base services' interfaces
=========================


.. autoclass:: agatsuma.interfaces.IModelSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.ISettingsBackendSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.IStorageSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.IModelSpell
   :members:
   :inherited-members:


Web-related spells
==================

.. autoclass:: agatsuma.web.tornado.interfaces.ISessionHandler
   :members:
   :inherited-members:

Other interfaces
****************

.. autoclass:: agatsuma.interfaces.AbstractSettingsBackend
   :members:
   :inherited-members:

"""

from abstract_spell import AbstractSpell
from abstract_core_extension import AbstractCoreExtension

from i_model_spell import IModelSpell
from i_filtering_spell import IFilteringSpell
from i_settings_backend_spell import ISettingsBackendSpell
from settings_backend import AbstractSettingsBackend
from i_pool_event_spell import IPoolEventSpell
from i_storage_spell import IStorageSpell
from i_setup_spell import ISetupSpell
from i_internal_spell import IInternalSpell

__all__ = ["AbstractSpell",
           "AbstractCoreExtension",
           "IInternalSpell",
           "ISetupSpell",
           "IFilteringSpell",

           "IPoolEventSpell",

           "IModelSpell",
           "ISettingsBackendSpell",
           "AbstractSettingsBackend",
           "IStorageSpell",
          ]
