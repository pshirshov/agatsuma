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


.. autoclass:: agatsuma.interfaces.FilteringSpell
   :members:
   :inherited-members:


Multiprocessing core interfaces
===============================

.. autoclass:: agatsuma.interfaces.PoolEventSpell
   :members:
   :inherited-members:


Base services' interfaces
=========================


.. autoclass:: agatsuma.interfaces.ModelSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.SettingsBackendSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.StorageSpell
   :members:
   :inherited-members:

.. autoclass:: agatsuma.interfaces.ModelSpell
   :members:
   :inherited-members:


Web-related spells
==================

.. autoclass:: agatsuma.interfaces.SessionHandler
   :members:
   :inherited-members:

Other interfaces
****************

.. autoclass:: agatsuma.interfaces.SettingsBackend
   :members:
   :inherited-members:

"""

from abstract_spell import AbstractSpell
from model_spell import ModelSpell
from filtering_spell import FilteringSpell
from settings_backend_spell import SettingsBackendSpell
from settings_backend import SettingsBackend
from pool_event_spell import PoolEventSpell
from storage_spell import StorageSpell

# web-related
from session_handler import SessionHandler
from session import Session # for internal usage

__all__ = ["AbstractSpell",
           "FilteringSpell",

           "PoolEventSpell",

           "ModelSpell",
           "SettingsBackendSpell",
           "SettingsBackend",
           "StorageSpell"

           "Session", 
           "SessionHandler",
          ]
