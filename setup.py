#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from setuptools import setup, find_packages
from distribute_setup import use_setuptools

from agatsuma.core import Core
from agatsuma import log
from agatsuma.interfaces import AbstractSpell

use_setuptools()

core = Core(None, None)
log.newLogger("setup", logging.DEBUG)
spells = core.implementationsOf(AbstractSpell)

dependencies = []
for spell in spells:
    dependencies.extend(spell.requirements())
log.setup.info("The following dependencies are found: %s" % str(dependencies))


setup(
    name = "Agatsuma",
    version = Core.versionString,
    packages = find_packages(),
    install_requires = dependencies,

    #scripts = ['say_hello.py'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Fei Wong Reed",
    author_email = "feiwreed@gmail.com",
    description = "Modularity and flexibility for Tornado and others",
    license = "GPL3",
    keywords = "agatsuma modularity web framework dynamic imports",
    url = "http://agatsuma.ritsuka.org/",
)
