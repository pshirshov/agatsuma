.. Agatsuma documentation master file, created by
   sphinx-quickstart on Sat Jun 19 23:21:21 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. highlight:: python
   :linenothreshold: 5

Agatsuma: a bit of graceful magic
====================================

Agatsuma is a simple but powerful library providing the following functionality:

#. Universal extendible modular core able to traversing directories and load 
   different modules 
#. Useful services such as settings, logging, SQLAlchemy and MongoDB support, 
   pool of worker processes and more
#. Many usable extensions for 
   `Tornado Web Framework <http://www.tornadoweb.org/>`_ 
   such as URL building, sessions and more

Support for another frameworks is planned. 

Note that thougn Agatsuma is intended to be extension for Tornado 
Framework many Agatsuma's components may be used in projects that 
are not using Tornado and not even related to Web.

Key conception
===============

Most powerful Agatsuma's ideas are *dynamically loading modules*,
*hooks*, *callbacks* and *mix-ins*.

So applications using Agatsuma consists of tons of small modules
(named **spells**) that does everything.

Every spell can dramatically change all the aspects of application behavior,
every functionality may be turned on or off and application will 
change without any modifications of source code.


Contents
========

.. toctree::
   :maxdepth: 2

   core
   base_services
   interfaces
   tornado

Quick start: setting up application
===================================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
