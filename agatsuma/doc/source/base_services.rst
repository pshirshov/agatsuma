Agatsuma base services
######################

.. _std-entry-points:

Entry points
******************

Settings
******************

Logging
******************

Data storages
******************

.. autoclass:: agatsuma.spells.storage_drivers.core_sqla.SQLASpell

Improved Library Setup
**********************

.. _std-distutils:

Agatsuma using `Distribute <http://packages.python.org/distribute/>`_
(Setuptools fork) as distribution system.

Every Agatsuma's spell can require some dependencies which may be handled by
Distribute. So Agatsuma's internal spells using same way to require
dependencies.
